from typing import List, Optional
import uuid
from datetime import datetime

class Meeting:
    def __init__(self, title: str = "", obj: str = "", description: str = "", invited_employees: List[str] = None, password: str = "", created_by: str = ""):
        self.__DatabaseID: Optional[int] = None  # ID from SAVING_SERVER database
        self.__ID: str = str(uuid.uuid4())  # meeting_id (UUID)
        self.__Title: str = title
        self.__Object: str = obj
        self.__InvitationLink: str = f"http://localhost:7053/room/{self.__ID}"
        self.__LogPath: str = ""
        self.__Description: str = description
        self.__InvitedEmployeesList: List = invited_employees if invited_employees else []
        self.__CreatedAt: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.__Password: str = password
        self.__CreatedBy: str = created_by
        self.__IsActive: bool = True
        self.__StartedAt: Optional[str] = None
        self.__EndedAt: Optional[str] = None
        
    
    def getID(self) -> str:
        return self.__ID
    
    def setID(self, ID: str) -> None:
        self.__ID = ID
    
    def getTitle(self) -> str:
        return self.__Title
    
    def setTitle(self, Title: str) -> None:
        self.__Title = Title
    
    def getObject(self) -> str:
        return self.__Object
    
    def setObject(self, Object: str) -> None:
        self.__Object = Object
    
    def getInvitationLink(self) -> str:
        return self.__InvitationLink
    
    def setInvitationLink(self, InvitationLink: str) -> None:
        self.__InvitationLink = InvitationLink
    
    def getLogPath(self) -> str:
        return self.__LogPath
    
    def setLogPath(self, LogPath: str) -> None:
        self.__LogPath = LogPath
    
    def getDescription(self) -> str:
        return self.__Description
    
    def setDescription(self, Description: str) -> None:
        self.__Description = Description
    
    def getInvitedEmployeesList(self) -> List:
        return self.__InvitedEmployeesList
    
    def setInvitedEmployeesList(self, InvitedEmployeesList: List) -> None:
        self.__InvitedEmployeesList = InvitedEmployeesList
    
    def getCreatedAt(self) -> str:
        return self.__CreatedAt
    
    def setCreatedAt(self, CreatedAt: str) -> None:
        self.__CreatedAt = CreatedAt
    
    def getPassword(self) -> str:
        return self.__Password
    
    def setPassword(self, Password: str) -> None:
        self.__Password = Password
    
    def getDatabaseID(self) -> Optional[int]:
        return self.__DatabaseID
    
    def setDatabaseID(self, DatabaseID: int) -> None:
        self.__DatabaseID = DatabaseID
    
    def getCreatedBy(self) -> str:
        return self.__CreatedBy
    
    def setCreatedBy(self, CreatedBy: str) -> None:
        self.__CreatedBy = CreatedBy
    
    def getIsActive(self) -> bool:
        return self.__IsActive
    
    def setIsActive(self, IsActive: bool) -> None:
        self.__IsActive = IsActive
    
    def getStartedAt(self) -> Optional[str]:
        return self.__StartedAt
    
    def setStartedAt(self, StartedAt: str) -> None:
        self.__StartedAt = StartedAt
    
    def getEndedAt(self) -> Optional[str]:
        return self.__EndedAt
    
    def setEndedAt(self, EndedAt: str) -> None:
        self.__EndedAt = EndedAt
    
    def to_dict(self) -> dict:
        """Convert Meeting object to dictionary for API requests"""
        return {
            "title": self.__Title,
            "object": self.__Object,
            "description": self.__Description,
            "invited_employees": self.__InvitedEmployeesList,
            "password": self.__Password,
            "created_by": self.__CreatedBy
        }
    
    @staticmethod
    def from_api_response(data: dict) -> 'Meeting':
        """Create Meeting object from SAVING_SERVER API response"""
        meeting = Meeting(
            title=data.get('title', ''),
            obj=data.get('object', ''),
            description=data.get('description', ''),
            invited_employees=data.get('invited_employees_list', []),
            password=data.get('password', ''),
            created_by=data.get('created_by', '')
        )
        meeting.setDatabaseID(data.get('id'))
        meeting.setID(data.get('meeting_id', ''))
        meeting.setInvitationLink(data.get('invitation_link', ''))
        meeting.setLogPath(data.get('log_path', ''))
        meeting.setCreatedAt(data.get('created_at', ''))
        meeting.setIsActive(data.get('is_active', True))
        meeting.setStartedAt(data.get('started_at'))
        meeting.setEndedAt(data.get('ended_at'))
        return meeting
