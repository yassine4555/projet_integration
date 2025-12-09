from __future__ import annotations
from dataclasses import dataclass

from modeles.department import Department
from modeles.role import ROLE



class User:


    def __init__(self,Email=None, FirstName=None, LastName=None,  ID=None,DateOfBirth=None,  Address=None , EmployeesList=None,Department=None,Role=ROLE.GUEST) :
        self.ID = ID
        self.FirstName = FirstName
        self.LastName = LastName
        self.DateOfBirth = DateOfBirth
        self.Email = Email
        self.Address = Address
        # Ensure EmployeesList is always a list
        self.EmployeesList = EmployeesList if EmployeesList is not None else []
        self.Department = Department
        self.Role = Role

    def getId(self):
        return self.ID

    def setId(self, id_value):
        self.ID = id_value

    def getFirstName(self):
        return self.FirstName

    def setFirstName(self, first_name):
        self.FirstName = first_name

    def getLastName(self):
        return self.LastName

    def setLastName(self, last_name):
        self.LastName = last_name

    def getDateOfBirth(self):
        return self.DateOfBirth

    def setDateOfBirth(self, dob):
        self.DateOfBirth = dob

    def getEmail(self):
        return self.Email

    def setEmail(self, email):
        self.Email = email

    def getAddress(self):
        return self.Address

    def setAddress(self, address):
        self.Address = address

    def getEmployeesList(self):
        return self.EmployeesList

    def setEmployeesList(self, employees):
        self.EmployeesList = list(employees)
    def getDepartment(self):
        return self.Department

    def setDepartment(self, department: Department):
        self.Department = department

    def getRole(self):
        return self.Role

    def setRole(self, role: ROLE):
        self.Role = role
    def __str__(self):
        return "User(ID=%r, FirstName=%r, LastName=%r)" % (self.ID, self.FirstName, self.LastName)
    def to_dict(self):
        """Convert User object to dictionary for JSON serialization"""
        return {
            "Email": self.Email,
            "FirstName": self.FirstName,
            "LastName": self.LastName,
            "ID": self.ID,
            "DateOfBirth": self.DateOfBirth,
            "Address": self.Address,
            "EmployeesList": [emp.to_dict() if hasattr(emp, 'to_dict') else emp for emp in self.EmployeesList],  # ✅ Serialize nested users
            "Role": self.Role.value if hasattr(self.Role, 'value') else self.Role,
            "Department": self.Department.value if hasattr(self.Department, 'value') else self.Department
        }

    @classmethod
    def from_dict(cls, data):
        """Create User object from dictionary"""
        return cls(
            Email=data.get('Email'),
            FirstName=data.get('FirstName'),
            LastName=data.get('LastName'),
            ID=data.get('ID'),
            DateOfBirth=data.get('DateOfBirth'),
            Address=data.get('Address'),
            EmployeesList=data.get('EmployeesList', []),
            Role=data.get('Role', ROLE.EMPLOYER),
            Department=data.get('Department', "DEPARTMENT.IT")
        )
