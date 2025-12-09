import requests
import os
from dotenv import load_dotenv

load_dotenv()

class FileHelper:
    HEADERS = {"X-Internal-Key": "nexus-internal-secret-key-123"}

    def __init__(self):
        self.saving_server = os.getenv('SAVING_SERVER')
        self.base_url = f"http://{self.saving_server}"
    
    def upload_file(self, file, user_email):
        """
        Upload a file to the saving server
        
        Args:
            file: File object from Flask request
            user_email: Email of the user uploading the file
            
        Returns:
            dict: Response from the saving server
        """
        try:
            files = {'file': (file.filename, file.stream, file.content_type)}
            data = {'user_email': user_email}
            
            response = requests.post(
                f"{self.base_url}/file/upload",
                files=files,
                headers=FileHelper.HEADERS,
                data=data
            )
            
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'data': response.json() if response.status_code == 200 else response.text
            }
        except Exception as e:
            return {
                'success': False,
                'status_code': 500,
                'error': str(e)
            }
    
    def get_file(self, filename):
        """
        Get a specific file from the saving server
        
        Args:
            filename: Name of the file to retrieve
            
        Returns:
            dict: Response containing file data or error
        """
        try:
            response = requests.get(
                f"{self.base_url}/file/get/{filename}",
                                headers=FileHelper.HEADERS
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'status_code': response.status_code,
                    'data': response.content,
                    'content_type': response.headers.get('Content-Type'),
                    'filename': filename
                }
            else:
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'error': response.text
                }
        except Exception as e:
            return {
                'success': False,
                'status_code': 500,
                'error': str(e)
            }
    
    def get_all_files(self):
        """
        Get all file names from the saving server
        
        Returns:
            dict: Response containing list of files or error
        """
        try:
            response = requests.get(
                f"{self.base_url}/file/getAll",
                                headers=FileHelper.HEADERS,

            )
            
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'data': response.json() if response.status_code == 200 else response.text
            }
        except Exception as e:
            return {
                'success': False,
                'status_code': 500,
                'error': str(e)
            }
