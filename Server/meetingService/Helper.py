from typing import List, Optional, Dict
from meeting import Meeting
import requests
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)


class MeetHelper:
    """
    Helper class to manage meetings through SAVING_SERVER API
    Following the same pattern as dataService/Helper.py and authService
    """
    
    HEADERS = {"X-Internal-Key": "nexus-internal-secret-key-123"}
    SAVING_SERVER = os.getenv("SAVING_SERVER")
    BASE_URL = f"{SAVING_SERVER}"
    
    # Keep local cache of meetings for quick access (optional)
    __meetings_cache: Dict[str, Meeting] = {}
    
    @staticmethod
    def createMeeting(meeting: Meeting) -> Optional[Meeting]:
        """
        Create a new meeting in SAVING_SERVER
        
        Args:
            meeting: Meeting object to create
            
        Returns:
            Meeting object with database ID if successful, None otherwise
        """
        try:
            # Prepare request data
            data = meeting.to_dict()
            
            # POST to SAVING_SERVER
            response = requests.post(
                f"{MeetHelper.BASE_URL}/meetings/",
                json=data,
                headers=MeetHelper.HEADERS
            )
            
            if response.status_code in [200, 201]:
                # Update meeting with response data
                response_data = response.json()
                meeting = Meeting.from_api_response(response_data)
                
                # Cache the meeting
                MeetHelper.__meetings_cache[meeting.getID()] = meeting
                
                logger.info(f"Meeting created successfully: {meeting.getID()}")
                return meeting
            else:
                logger.error(f"Failed to create meeting: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating meeting: {str(e)}")
            return None
    
    @staticmethod
    def getMeetingByID(meeting_id: str) -> Optional[Meeting]:
        """
        Get meeting by ID from SAVING_SERVER
        
        Args:
            meeting_id: UUID of the meeting
            
        Returns:
            Meeting object if found, None otherwise
        """
        # Check cache first
        if meeting_id in MeetHelper.__meetings_cache:
            return MeetHelper.__meetings_cache[meeting_id]
        
        try:
            response = requests.get(
                f"{MeetHelper.BASE_URL}/meetings/{meeting_id}",
                headers=MeetHelper.HEADERS
            )
            print("response from saving : ",response.json())
            if response.status_code == 200:
                meeting = Meeting.from_api_response(response.json())
                MeetHelper.__meetings_cache[meeting_id] = meeting
                return meeting
            else:
                logger.error(f"Meeting not found: {meeting_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting meeting: {str(e)}")
            return None
    
    @staticmethod
    def getAllMeetings(user_email: Optional[str] = None, is_active: Optional[bool] = None) -> List[Meeting]:
        """
        Get all meetings with optional filters
        
        Args:
            user_email: Filter by creator or invited user
            is_active: Filter by active status
            
        Returns:
            List of Meeting objects
        """
        try:
            params = {}
            if user_email:
                params['user_email'] = user_email
            if is_active is not None:
                params['is_active'] = str(is_active).lower()
            
            response = requests.get(
                f"{MeetHelper.BASE_URL}/meetings/",
                headers=MeetHelper.HEADERS,
                params=params
            )
            
            if response.status_code == 200:
                meetings_data = response.json().get('data', [])
                meetings = [Meeting.from_api_response(m) for m in meetings_data]
                
                # Update cache
                for meeting in meetings:
                    MeetHelper.__meetings_cache[meeting.getID()] = meeting
                
                return meetings
            else:
                logger.error(f"Failed to get meetings: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting meetings: {str(e)}")
            return []
    
    @staticmethod
    def updateMeeting(meeting_id: str, updates: dict) -> bool:
        """
        Update meeting details
        
        Args:
            meeting_id: UUID of the meeting
            updates: Dictionary of fields to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.put(
                f"{MeetHelper.BASE_URL}/meetings/{meeting_id}",
                json=updates,
                headers=MeetHelper.HEADERS
            )
            
            if response.status_code == 200:
                # Invalidate cache
                if meeting_id in MeetHelper.__meetings_cache:
                    del MeetHelper.__meetings_cache[meeting_id]
                logger.info(f"Meeting updated: {meeting_id}")
                return True
            else:
                logger.error(f"Failed to update meeting: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating meeting: {str(e)}")
            return False
    
    @staticmethod
    def startMeeting(meeting_id: str) -> bool:
        """
        Mark meeting as started
        
        Args:
            meeting_id: UUID of the meeting
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.post(
                f"{MeetHelper.BASE_URL}/meetings/{meeting_id}/start",
                headers=MeetHelper.HEADERS
            )
            
            if response.status_code == 200:
                # Invalidate cache
                if meeting_id in MeetHelper.__meetings_cache:
                    del MeetHelper.__meetings_cache[meeting_id]
                logger.info(f"Meeting started: {meeting_id}")
                return True
            else:
                logger.error(f"Failed to start meeting: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error starting meeting: {str(e)}")
            return False
    
    @staticmethod
    def endMeeting(meeting_id: str) -> bool:
        """
        Mark meeting as ended
        
        Args:
            meeting_id: UUID of the meeting
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.post(
                f"{MeetHelper.BASE_URL}/meetings/{meeting_id}/end",
                headers=MeetHelper.HEADERS
            )
            
            if response.status_code == 200:
                # Invalidate cache
                if meeting_id in MeetHelper.__meetings_cache:
                    del MeetHelper.__meetings_cache[meeting_id]
                logger.info(f"Meeting ended: {meeting_id}")
                return True
            else:
                logger.error(f"Failed to end meeting: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error ending meeting: {str(e)}")
            return False
    
    @staticmethod
    def addLogEntry(meeting_id: str, log_entry: str) -> bool:
        """
        Add a log entry to the meeting log
        
        Args:
            meeting_id: UUID of the meeting
            log_entry: Log entry text
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.post(
                f"{MeetHelper.BASE_URL}/meetings/{meeting_id}/log",
                json={"log_entry": log_entry},
                headers=MeetHelper.HEADERS
            )
            
            if response.status_code == 200:
                return True
            else:
                logger.error(f"Failed to add log entry: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding log entry: {str(e)}")
            return False
    
    @staticmethod
    def getMeetingLog(meeting_id: str) -> Optional[str]:
        """
        Get meeting log content
        
        Args:
            meeting_id: UUID of the meeting
            
        Returns:
            Log content as string if successful, None otherwise
        """
        try:
            response = requests.get(
                f"{MeetHelper.BASE_URL}/meetings/{meeting_id}/log",
                headers=MeetHelper.HEADERS
            )
            
            if response.status_code == 200:
                return response.json().get('log_content')
            else:
                logger.error(f"Failed to get log: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting log: {str(e)}")
            return None
    
    @staticmethod
    def deleteMeeting(meeting_id: str) -> bool:
        """
        Delete (soft delete) a meeting
        
        Args:
            meeting_id: UUID of the meeting
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.delete(
                f"{MeetHelper.BASE_URL}/meetings/{meeting_id}",
                headers=MeetHelper.HEADERS
            )
            
            if response.status_code == 200:
                # Remove from cache
                if meeting_id in MeetHelper.__meetings_cache:
                    del MeetHelper.__meetings_cache[meeting_id]
                logger.info(f"Meeting deleted: {meeting_id}")
                return True
            else:
                logger.error(f"Failed to delete meeting: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting meeting: {str(e)}")
            return False
    
    # ========== Legacy Methods (kept for backward compatibility) ==========
    
    @staticmethod
    def addMeeting(meeting: Meeting) -> Optional[Meeting]:
        """Legacy method - use createMeeting instead"""
        return MeetHelper.createMeeting(meeting)
    
    @staticmethod
    def getMeetings() -> List[Meeting]:
        """Legacy method - use getAllMeetings instead"""
        return MeetHelper.getAllMeetings()
    
    @staticmethod    
    def addUserToMeeting(meeting_id: str, user_email: str) -> bool:
        """
        Add user to meeting's invited list
        
        Args:
            meeting_id: UUID of the meeting
            user_email: Email of user to add
            
        Returns:
            True if successful, False otherwise
        """
        meeting = MeetHelper.getMeetingByID(meeting_id)
        if not meeting:
            return False
        
        invited = meeting.getInvitedEmployeesList()
        if user_email in invited:
            return True  # Already invited
        
        invited.append(user_email)
        return MeetHelper.updateMeeting(meeting_id, {"invited_employees": invited})
    
    @staticmethod
    def verifyUserInMeeting(meeting_id: str, user_email: str) -> bool:
        """
        Verify if user is invited to meeting
        
        Args:
            meeting_id: UUID of the meeting
            user_email: Email of user to verify
            
        Returns:
            True if user is invited, False otherwise
        """
        meeting = MeetHelper.getMeetingByID(meeting_id)
        if not meeting:
            return False
        
        return user_email in meeting.getInvitedEmployeesList()
    
    @staticmethod
    def verifyMeetingPassword(meeting_id: str, password: str) -> bool:
        """
        Verify meeting password
        
        Args:
            meeting_id: UUID of the meeting
            password: Password to verify
            
        Returns:
            True if password is correct, False otherwise
        """
        meeting = MeetHelper.getMeetingByID(meeting_id)
        if not meeting:
            return False
        
        return meeting.getPassword() == password




