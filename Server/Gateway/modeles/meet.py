from typing import List

class Meeting:
    def __init__(self, ID: str, Title: str, Object: str, InvitationLink: str, 
                 LogPath: str, Description: str, InvitedEmployeesList: List[str], 
                 Creator: str):
        """
        Initialize a Meeting object
        
        Args:
            ID: Unique identifier for the meeting
            Title: Meeting title
            Object: Meeting object/subject
            InvitationLink: Link to join the meeting
            LogPath: Path to meeting log file
            Description: Meeting description
            InvitedEmployeesList: List of employee IDs invited to the meeting
            Creator: Email or ID of the meeting creator
        """
        self.__ID = ID
        self.__Title = Title
        self.__Object = Object
        self.__InvitationLink = InvitationLink
        self.__LogPath = LogPath
        self.__Description = Description
        self.__InvitedEmployeesList = InvitedEmployeesList if InvitedEmployeesList else []
        self.__Creator = Creator

    # Getter methods
    def getID(self) -> str:
        """Get meeting ID"""
        return self.__ID

    def getTitle(self) -> str:
        """Get meeting title"""
        return self.__Title

    def getObject(self) -> str:
        """Get meeting object/subject"""
        return self.__Object

    def getInvitationLink(self) -> str:
        """Get meeting invitation link"""
        return self.__InvitationLink

    def getLogPath(self) -> str:
        """Get meeting log path"""
        return self.__LogPath

    def getDescription(self) -> str:
        """Get meeting description"""
        return self.__Description

    def getInvitedEmployeesList(self) -> List[str]:
        """Get list of invited employees"""
        return self.__InvitedEmployeesList

    def getCreator(self) -> str:
        """Get meeting creator"""
        return self.__Creator

    # Setter methods
    def setID(self, ID: str) -> None:
        """Set meeting ID"""
        self.__ID = ID

    def setTitle(self, Title: str) -> None:
        """Set meeting title"""
        self.__Title = Title

    def setObject(self, Object: str) -> None:
        """Set meeting object/subject"""
        self.__Object = Object

    def setInvitationLink(self, InvitationLink: str) -> None:
        """Set meeting invitation link"""
        self.__InvitationLink = InvitationLink

    def setLogPath(self, LogPath: str) -> None:
        """Set meeting log path"""
        self.__LogPath = LogPath

    def setDescription(self, Description: str) -> None:
        """Set meeting description"""
        self.__Description = Description

    def setInvitedEmployeesList(self, InvitedEmployeesList: List[str]) -> None:
        """Set list of invited employees"""
        self.__InvitedEmployeesList = InvitedEmployeesList

    def setCreator(self, Creator: str) -> None:
        """Set meeting creator"""
        self.__Creator = Creator

    # Utility methods
    def to_dict(self) -> dict:
        """Convert Meeting object to dictionary for JSON serialization"""
        return {
            "ID": self.__ID,
            "Title": self.__Title,
            "Object": self.__Object,
            "InvitationLink": self.__InvitationLink,
            "LogPath": self.__LogPath,
            "Description": self.__Description,
            "InvitedEmployeesList": self.__InvitedEmployeesList,
            "Creator": self.__Creator
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Create Meeting object from dictionary"""
        return cls(
            ID=data.get('ID'),
            Title=data.get('Title'),
            Object=data.get('Object'),
            InvitationLink=data.get('InvitationLink'),
            LogPath=data.get('LogPath'),
            Description=data.get('Description'),
            InvitedEmployeesList=data.get('InvitedEmployeesList', []),
            Creator=data.get('Creator')
        )

    def __repr__(self) -> str:
        """String representation of Meeting object"""
        return f"Meeting(ID={self.__ID}, Title={self.__Title}, Creator={self.__Creator})"

    def __str__(self) -> str:
        """User-friendly string representation"""
        return f"{self.__Title} - {self.__Object} (Created by: {self.__Creator})"