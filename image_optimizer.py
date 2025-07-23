#!/usr/bin/env python3
"""
Image Optimizer GUI Application
Converts images to WEBP and/or AVIF formats with resizing and quality options.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
from pathlib import Path
from PIL import Image, ImageOps
import threading
import queue
import time
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed
import functools

def process_single_image(args):
    """Process a single image - designed to work with multiprocessing"""
    try:
        file_path, source_path, settings = args
        
        # Unpack settings
        webp_folder = settings['webp_folder']
        avif_folder = settings['avif_folder']
        convert_webp = settings['convert_webp']
        convert_avif = settings['convert_avif']
        webp_quality = settings['webp_quality']
        avif_quality = settings['avif_quality']
        max_width = settings['max_width']
        max_height = settings['max_height']
        
        relative_path = file_path.relative_to(source_path)
        results = {'file': relative_path, 'success': True, 'messages': []}
        
        # Open and process image with optimization
        with Image.open(file_path) as img:
            # Optimize loading for large images
            img.load()
            
            # Convert to RGB if necessary (optimized)
            if img.mode in ('RGBA', 'LA'):
                # Create white background only once
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            elif img.mode == 'P':
                # Handle palette mode
                img = img.convert('RGB')
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize if needed
            img = resize_image_standalone(img, max_width, max_height)
            
            # Save formats
            if convert_webp:
                webp_path = webp_folder / relative_path.with_suffix('.webp')
                webp_path.parent.mkdir(parents=True, exist_ok=True)
                # Use optimized save parameters
                img.save(webp_path, 'WEBP', quality=webp_quality, optimize=True, method=6)
                results['messages'].append(f"Saved WEBP: {webp_path.relative_to(source_path)}")
            
            if convert_avif:
                avif_path = avif_folder / relative_path.with_suffix('.avif')
                avif_path.parent.mkdir(parents=True, exist_ok=True)
                try:
                    # Use optimized AVIF parameters
                    img.save(avif_path, 'AVIF', quality=avif_quality, optimize=True, speed=6)
                    results['messages'].append(f"Saved AVIF: {avif_path.relative_to(source_path)}")
                except Exception as e:
                    results['messages'].append(f"Failed to save AVIF for {relative_path}: {str(e)}")
        
        return results
        
    except Exception as e:
        return {'file': relative_path, 'success': False, 'messages': [f"Error processing {relative_path}: {str(e)}"]}

def resize_image_standalone(img, max_width, max_height):
    """Standalone resize function for multiprocessing"""
    original_width, original_height = img.size
    max_w = max_width if max_width > 0 else None
    max_h = max_height if max_height > 0 else None
    
    # If no limits set, return original
    if not max_w and not max_h:
        return img
    
    # Don't enlarge images
    if max_w and original_width <= max_w and max_h and original_height <= max_h:
        return img
    if max_w and not max_h and original_width <= max_w:
        return img
    if max_h and not max_w and original_height <= max_h:
        return img
    
    # Calculate new dimensions
    if max_w and max_h:
        # Both dimensions specified - maintain aspect ratio
        ratio = min(max_w / original_width, max_h / original_height)
    elif max_w:
        # Only width specified
        ratio = max_w / original_width
    else:
        # Only height specified
        ratio = max_h / original_height
    
    # Don't enlarge
    if ratio >= 1:
        return img
        
    new_width = int(original_width * ratio)
    new_height = int(original_height * ratio)
    
    return img.resize((new_width, new_height), Image.Resampling.LANCZOS)

class ImageOptimizer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Rol's Image Optimizer - WEBP/AVIF Converter")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Variables
        self.source_folder = tk.StringVar()
        self.convert_webp = tk.BooleanVar(value=True)
        self.convert_avif = tk.BooleanVar(value=True)
        self.max_width = tk.IntVar(value=0)  # 0 means no limit
        self.max_height = tk.IntVar(value=0)  # 0 means no limit
        self.webp_quality = tk.IntVar(value=80)
        self.avif_quality = tk.IntVar(value=80)
        
        # Performance settings
        self.use_multiprocessing = tk.BooleanVar(value=True)
        self.max_workers = tk.IntVar(value=min(8, multiprocessing.cpu_count()))
        
        # Progress tracking
        self.progress_queue = queue.Queue()
        self.is_processing = False
        self.stop_processing = False
        self.executor = None
        
        self.setup_ui()
        self.check_progress()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Source folder selection
        ttk.Label(main_frame, text="Source Folder:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        folder_frame = ttk.Frame(main_frame)
        folder_frame.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        folder_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(folder_frame, textvariable=self.source_folder, width=50).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(folder_frame, text="Browse", command=self.browse_folder).grid(row=0, column=1)
        
        # Format selection
        format_frame = ttk.LabelFrame(main_frame, text="Output Formats", padding="10")
        format_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Checkbutton(format_frame, text="Convert to WEBP", variable=self.convert_webp).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(format_frame, text="Convert to AVIF", variable=self.convert_avif).grid(row=0, column=1, sticky=tk.W)
        
        # Resize settings
        resize_frame = ttk.LabelFrame(main_frame, text="Resize Settings (0 = no limit)", padding="10")
        resize_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(resize_frame, text="Max Width:").grid(row=0, column=0, sticky=tk.W)
        ttk.Spinbox(resize_frame, from_=0, to=4000, width=10, textvariable=self.max_width).grid(row=0, column=1, padx=5)
        
        ttk.Label(resize_frame, text="Max Height:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        ttk.Spinbox(resize_frame, from_=0, to=4000, width=10, textvariable=self.max_height).grid(row=0, column=3, padx=5)
        
        # Quality settings
        quality_frame = ttk.LabelFrame(main_frame, text="Quality Settings (1-100)", padding="10")
        quality_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # WEBP Quality
        ttk.Label(quality_frame, text="WEBP Quality:").grid(row=0, column=0, sticky=tk.W)
        ttk.Scale(quality_frame, from_=1, to=100, orient=tk.HORIZONTAL, variable=self.webp_quality, length=120).grid(row=0, column=1, padx=5)
        webp_quality_entry = ttk.Entry(quality_frame, textvariable=self.webp_quality, width=5)
        webp_quality_entry.grid(row=0, column=2, padx=5)
        
        # AVIF Quality  
        ttk.Label(quality_frame, text="AVIF Quality:").grid(row=1, column=0, sticky=tk.W)
        ttk.Scale(quality_frame, from_=1, to=100, orient=tk.HORIZONTAL, variable=self.avif_quality, length=120).grid(row=1, column=1, padx=5)
        avif_quality_entry = ttk.Entry(quality_frame, textvariable=self.avif_quality, width=5)
        avif_quality_entry.grid(row=1, column=2, padx=5)
        
        # Quality validation will be done at processing time instead of on every keystroke
        
        # Performance settings
        perf_frame = ttk.LabelFrame(main_frame, text="Performance Settings", padding="10")
        perf_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Checkbutton(perf_frame, text="Use Multiprocessing (Faster)", variable=self.use_multiprocessing).grid(row=0, column=0, sticky=tk.W)
        
        ttk.Label(perf_frame, text="Max Workers:").grid(row=0, column=1, sticky=tk.W, padx=(20, 5))
        ttk.Spinbox(perf_frame, from_=1, to=16, width=5, textvariable=self.max_workers).grid(row=0, column=2)
        ttk.Label(perf_frame, text=f"(CPU cores: {multiprocessing.cpu_count()})").grid(row=0, column=3, sticky=tk.W, padx=(5, 0))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Process button
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=10)
        
        self.process_button = ttk.Button(button_frame, text="Start Optimization", command=self.start_processing)
        self.process_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_processing_request, state="disabled")
        self.stop_button.grid(row=0, column=1)
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Processing Log", padding="10")
        log_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(7, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, width=70, height=15)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def browse_folder(self):
        """Open folder selection dialog"""
        folder = filedialog.askdirectory()
        if folder:
            self.source_folder.set(folder)
    
    def stop_processing_request(self):
        """Request to stop the current processing"""
        self.stop_processing = True
        self.log_message("Stop requested - finishing current images...")
        self.stop_button.config(state="disabled")
        
        # If using multiprocessing, shutdown the executor
        if self.executor:
            self.executor.shutdown(wait=False)
            
    def log_message(self, message):
        """Add message to log area"""
        self.log_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def validate_quality_values(self):
        """Validate quality values before processing"""
        errors = []
        
        try:
            webp_qual = self.webp_quality.get()
            if webp_qual < 1 or webp_qual > 100:
                errors.append(f"WEBP quality must be between 1-100 (current: {webp_qual})")
        except tk.TclError:
            errors.append("WEBP quality must be a valid number between 1-100")
            
        try:
            avif_qual = self.avif_quality.get()
            if avif_qual < 1 or avif_qual > 100:
                errors.append(f"AVIF quality must be between 1-100 (current: {avif_qual})")
        except tk.TclError:
            errors.append("AVIF quality must be a valid number between 1-100")
            
        return errors
    
    def start_processing(self):
        """Start the image processing in a separate thread"""
        if self.is_processing:
            return
            
        if not self.source_folder.get():
            messagebox.showerror("Error", "Please select a source folder")
            return
            
        if not self.convert_webp.get() and not self.convert_avif.get():
            messagebox.showerror("Error", "Please select at least one output format")
            return
            
        # Validate quality values
        quality_errors = self.validate_quality_values()
        if quality_errors:
            error_msg = "Invalid quality settings:\n" + "\n".join(quality_errors)
            messagebox.showerror("Quality Error", error_msg)
            return
            
        self.is_processing = True
        self.stop_processing = False
        self.process_button.config(text="Processing...", state="disabled")
        self.stop_button.config(state="normal")
        
        # Reset progress bar to determinate mode
        self.progress.config(mode='determinate', value=0)
        self.log_text.delete(1.0, tk.END)
        
        # Start processing thread
        if self.use_multiprocessing.get():
            thread = threading.Thread(target=self.process_images_multiprocessed)
        else:
            thread = threading.Thread(target=self.process_images_single)
        thread.daemon = True
        thread.start()
        
    def process_images_multiprocessed(self):
        """Process all images using multiprocessing for better performance"""
        try:
            source_path = Path(self.source_folder.get())
            
            if not source_path.exists():
                self.progress_queue.put(("error", "Source folder does not exist"))
                return
                
            # Supported image formats
            supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif', '.webp'}
            
            # Create output folders
            webp_folder = source_path / "webp"
            avif_folder = source_path / "avif"
            
            convert_webp = self.convert_webp.get()
            convert_avif = self.convert_avif.get()
            
            if convert_webp:
                webp_folder.mkdir(exist_ok=True)
                self.progress_queue.put(("log", f"Created WEBP output folder"))
                
            if convert_avif:
                avif_folder.mkdir(exist_ok=True)
                self.progress_queue.put(("log", f"Created AVIF output folder"))
            
            # Find all image files
            image_files = []
            for file_path in source_path.rglob("*"):
                if (file_path.is_file() and 
                    file_path.suffix.lower() in supported_formats and
                    "webp" not in file_path.parts and 
                    "avif" not in file_path.parts):
                    image_files.append(file_path)
            
            total_files = len(image_files)
            self.progress_queue.put(("log", f"Found {total_files} image files to process"))
            self.progress_queue.put(("progress_total", total_files))
            
            if not image_files:
                self.progress_queue.put(("error", "No supported image files found"))
                return
            
            # Prepare settings for multiprocessing
            settings = {
                'webp_folder': webp_folder,
                'avif_folder': avif_folder,
                'convert_webp': convert_webp,
                'convert_avif': convert_avif,
                'webp_quality': self.webp_quality.get(),
                'avif_quality': self.avif_quality.get(),
                'max_width': self.max_width.get(),
                'max_height': self.max_height.get(),
            }
            
            # Prepare arguments for multiprocessing
            process_args = [(file_path, source_path, settings) for file_path in image_files]
            
            # Use multiprocessing
            max_workers = min(self.max_workers.get(), len(image_files))
            self.progress_queue.put(("log", f"Using {max_workers} worker processes"))
            
            processed_count = 0
            start_time = time.time()
            
            self.executor = ProcessPoolExecutor(max_workers=max_workers)
            try:
                # Submit all tasks
                future_to_file = {self.executor.submit(process_single_image, args): args[0] 
                                 for args in process_args}
                
                # Process completed tasks
                for future in as_completed(future_to_file):
                    # Check if stop was requested
                    if self.stop_processing:
                        self.progress_queue.put(("log", "Processing stopped by user"))
                        break
                        
                    try:
                        result = future.result()
                        processed_count += 1
                        
                        # Update progress
                        progress_percent = (processed_count / total_files) * 100
                        self.progress_queue.put(("progress", progress_percent))
                        
                        # Log messages (less frequently to avoid UI lag)
                        if processed_count % 5 == 0 or processed_count <= 10:
                            elapsed = time.time() - start_time
                            rate = processed_count / elapsed if elapsed > 0 else 0
                            eta = (total_files - processed_count) / rate if rate > 0 else 0
                            self.progress_queue.put(("log", f"Progress: {processed_count}/{total_files} ({progress_percent:.1f}%) - {rate:.1f} img/sec - ETA: {eta:.0f}s"))
                        
                        # Log individual file messages for errors or first few files
                        if not result['success'] or processed_count <= 5:
                            for message in result['messages']:
                                self.progress_queue.put(("log", message))
                                
                    except Exception as e:
                        self.progress_queue.put(("log", f"Error processing file: {str(e)}"))
                        
            finally:
                self.executor.shutdown(wait=True)
                self.executor = None
            
            elapsed_time = time.time() - start_time
            avg_rate = processed_count / elapsed_time if elapsed_time > 0 else 0
            
            if self.stop_processing:
                self.progress_queue.put(("log", f"Processing stopped! {processed_count} images processed in {elapsed_time:.1f}s (avg: {avg_rate:.1f} img/sec)"))
                self.progress_queue.put(("stopped", ""))
            else:
                self.progress_queue.put(("log", f"Processing complete! {processed_count} images processed in {elapsed_time:.1f}s (avg: {avg_rate:.1f} img/sec)"))
                self.progress_queue.put(("complete", ""))
            
        except Exception as e:
            self.progress_queue.put(("error", f"Unexpected error: {str(e)}"))
    
    def process_images_single(self):
        """Original single-threaded processing (fallback)"""
        try:
            source_path = Path(self.source_folder.get())
            
            if not source_path.exists():
                self.progress_queue.put(("error", "Source folder does not exist"))
                return
                
            # Supported image formats
            supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif', '.webp'}
            
            # Create output folders
            webp_folder = source_path / "webp"
            avif_folder = source_path / "avif"
            
            if self.convert_webp.get():
                webp_folder.mkdir(exist_ok=True)
                self.progress_queue.put(("log", f"Created WEBP output folder"))
                
            if self.convert_avif.get():
                avif_folder.mkdir(exist_ok=True)
                self.progress_queue.put(("log", f"Created AVIF output folder"))
            
            # Find all image files
            image_files = []
            for file_path in source_path.rglob("*"):
                if (file_path.is_file() and 
                    file_path.suffix.lower() in supported_formats and
                    "webp" not in file_path.parts and 
                    "avif" not in file_path.parts):
                    image_files.append(file_path)
            
            total_files = len(image_files)
            self.progress_queue.put(("log", f"Found {total_files} image files to process"))
            self.progress_queue.put(("progress_total", total_files))
            
            if not image_files:
                self.progress_queue.put(("error", "No supported image files found"))
                return
            
            # Process each image with optimizations (single-threaded)
            processed_count = 0
            webp_quality = self.webp_quality.get()
            avif_quality = self.avif_quality.get()
            convert_webp = self.convert_webp.get()
            convert_avif = self.convert_avif.get()
            start_time = time.time()
            
            for file_path in image_files:
                # Check if stop was requested
                if self.stop_processing:
                    self.progress_queue.put(("log", "Processing stopped by user"))
                    break
                    
                try:
                    relative_path = file_path.relative_to(source_path)
                    
                    # Open and process image with optimization
                    with Image.open(file_path) as img:
                        # Optimize loading for large images
                        img.load()
                        
                        # Convert to RGB if necessary (optimized)
                        if img.mode in ('RGBA', 'LA'):
                            # Create white background only once
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            background.paste(img, mask=img.split()[-1])
                            img = background
                        elif img.mode == 'P':
                            # Handle palette mode
                            img = img.convert('RGB')
                        elif img.mode != 'RGB':
                            img = img.convert('RGB')
                        
                        # Resize if needed (once for both formats)
                        img = self.resize_image(img)
                        
                        # Save formats
                        if convert_webp:
                            webp_path = webp_folder / relative_path.with_suffix('.webp')
                            webp_path.parent.mkdir(parents=True, exist_ok=True)
                            # Use optimized save parameters
                            img.save(webp_path, 'WEBP', quality=webp_quality, optimize=True, method=6)
                        
                        if convert_avif:
                            avif_path = avif_folder / relative_path.with_suffix('.avif')
                            avif_path.parent.mkdir(parents=True, exist_ok=True)
                            try:
                                # Use optimized AVIF parameters
                                img.save(avif_path, 'AVIF', quality=avif_quality, optimize=True, speed=6)
                            except Exception as e:
                                self.progress_queue.put(("log", f"Failed to save AVIF for {relative_path}: {str(e)}"))
                    
                    processed_count += 1
                    
                    # Update progress
                    progress_percent = (processed_count / total_files) * 100
                    self.progress_queue.put(("progress", progress_percent))
                    
                    # Update progress periodically to keep UI responsive
                    if processed_count % 5 == 0:
                        elapsed = time.time() - start_time
                        rate = processed_count / elapsed if elapsed > 0 else 0
                        eta = (total_files - processed_count) / rate if rate > 0 else 0
                        self.progress_queue.put(("log", f"Progress: {processed_count}/{total_files} - {rate:.1f} img/sec - ETA: {eta:.0f}s"))
                    
                except Exception as e:
                    self.progress_queue.put(("log", f"Error processing {relative_path}: {str(e)}"))
            
            elapsed_time = time.time() - start_time
            avg_rate = processed_count / elapsed_time if elapsed_time > 0 else 0
            
            if self.stop_processing:
                self.progress_queue.put(("log", f"Processing stopped! {processed_count} images processed in {elapsed_time:.1f}s (avg: {avg_rate:.1f} img/sec)"))
                self.progress_queue.put(("stopped", ""))
            else:
                self.progress_queue.put(("log", f"Processing complete! {processed_count} images processed in {elapsed_time:.1f}s (avg: {avg_rate:.1f} img/sec)"))
                self.progress_queue.put(("complete", ""))
            
        except Exception as e:
            self.progress_queue.put(("error", f"Unexpected error: {str(e)}"))
    
    def resize_image(self, img):
        """Resize image based on max width and height settings"""
        original_width, original_height = img.size
        max_w = self.max_width.get() if self.max_width.get() > 0 else None
        max_h = self.max_height.get() if self.max_height.get() > 0 else None
        
        # If no limits set, return original
        if not max_w and not max_h:
            return img
        
        # Don't enlarge images
        if max_w and original_width <= max_w and max_h and original_height <= max_h:
            return img
        if max_w and not max_h and original_width <= max_w:
            return img
        if max_h and not max_w and original_height <= max_h:
            return img
        
        # Calculate new dimensions
        if max_w and max_h:
            # Both dimensions specified - maintain aspect ratio
            ratio = min(max_w / original_width, max_h / original_height)
        elif max_w:
            # Only width specified
            ratio = max_w / original_width
        else:
            # Only height specified
            ratio = max_h / original_height
        
        # Don't enlarge
        if ratio >= 1:
            return img
            
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)
        
        return img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def check_progress(self):
        """Check for messages from processing thread"""
        try:
            while True:
                msg_type, message = self.progress_queue.get_nowait()
                
                if msg_type == "log":
                    self.log_message(message)
                elif msg_type == "progress_total":
                    self.progress.config(maximum=message)
                elif msg_type == "progress":
                    self.progress.config(value=message)
                elif msg_type == "error":
                    self.log_message(f"ERROR: {message}")
                    messagebox.showerror("Error", message)
                    self.finish_processing()
                elif msg_type == "complete":
                    self.progress.config(value=self.progress.cget("maximum"))
                    self.log_message("All processing completed successfully!")
                    messagebox.showinfo("Complete", "Image optimization completed!")
                    self.finish_processing()
                elif msg_type == "stopped":
                    self.log_message("Processing was stopped by user")
                    messagebox.showinfo("Stopped", "Image processing was stopped")
                    self.finish_processing()
                    
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(50, self.check_progress)  # More frequent updates for better progress display
    
    def finish_processing(self):
        """Reset UI after processing is complete"""
        self.is_processing = False
        self.stop_processing = False
        self.process_button.config(text="Start Optimization", state="normal")
        self.stop_button.config(state="disabled")
        # Keep the progress bar showing completion
        # self.progress.config(mode='determinate', value=0)
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    """Main function"""
    try:
        # Check if PIL supports AVIF
        from PIL import Image
        supported_formats = Image.registered_extensions()
        if '.avif' not in supported_formats:
            print("Warning: AVIF format not supported. Please install pillow-avif-plugin")
        else:
            print("AVIF and WEBP formats are supported!")
    except ImportError:
        pass
    
    app = ImageOptimizer()
    app.run()

if __name__ == "__main__":
    # Ensure multiprocessing works correctly on all platforms
    multiprocessing.freeze_support()
    main()
