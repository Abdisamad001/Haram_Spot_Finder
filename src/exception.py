import os
import streamlit as st
from typing import Optional, Tuple, Any

class VideoProcessingError(Exception):
    """Exception for errors in video processing."""
    pass

class ImageProcessingError(Exception):
    """Exception for errors in image processing."""
    pass

class FileHandlingError(Exception):
    """Exception for errors in file handling."""
    pass

# video processing 
def handle_video_processing(model, temp_video_path: str) -> Tuple[Optional[str], Optional[bytes]]:
    """
    Process video with the YOLO model and handle any exceptions.
    
    Args:
        model: The YOLO model instance
        temp_video_path: Path to the temporary video file
        
    Returns:
        Tuple containing the output video path and video bytes
    """
    try:
        # Process and save video 
        results = model.predict(
            source=temp_video_path, 
            save=True,
            project="runs/detect",
            name="video_output"
        )
        
        # Find the saved video
        base_output_dir = "runs/detect/video_output"
        video_name = os.path.basename(temp_video_path)
        output_video_path = os.path.join(base_output_dir, video_name)
        
        # Check for the video file or any video in the directory
        if not os.path.exists(output_video_path) and os.path.exists(base_output_dir):
            video_files = [i for i in os.listdir(base_output_dir) if i.endswith(('.mp4', '.avi', '.mov'))]

            if video_files:
                output_video_path = os.path.join(base_output_dir, video_files[0])


        
        # Read the video file into memory to bypass file access issues
        if os.path.exists(output_video_path):
            with open(output_video_path, 'rb') as video_file:
                processed_video_bytes = video_file.read()
            return output_video_path, processed_video_bytes
        else:
            st.warning(f"Output video not found at expected path: {output_video_path}")
            return None, None
            
    except Exception as e:
        st.error(f"Error processing video: {str(e)}")
        raise VideoProcessingError(f"Failed to process video: {str(e)}")
    

# image processing 
def handle_image_processing(model, image):
    """
    Process image with the YOLO model and handle any exceptions.
    
    Args:
        model: The YOLO model
        image: PIL Image object
        
    Returns:
        Results from the model prediction of detectec places
    """
    try:
        # Convert to RGB format to ensure 3 channels
        image = image.convert('RGB')
        import numpy as np
        img_array = np.array(image)
        results = model.predict(img_array, save=False, imgsz=640)
        plotted = results[0].plot()
        return results, plotted
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        raise ImageProcessingError(f"Failed to process image: {str(e)}")
    
# handle_file_cleanup
def handle_file_cleanup(file_paths: list):
    """
    Clean up temporary files.
    
    Args:
        file_paths: List of file paths to remove
    """
    try:
        for path in file_paths:
            if path and os.path.exists(path):
                os.remove(path)
    except Exception as e:
        st.warning(f"Error cleaning up files: {str(e)}")
       