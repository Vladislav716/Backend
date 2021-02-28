from enum import Enum

class Visibility(str, Enum):
    open = "Open"
    restricted = "Restricted"


class SearchTypes(str, Enum):
    term = "Term"
    definition = "Definition"
    individual_contact = "IndividualContact"
    team_contact = "TeamContact"
    service = "Service"
    policy = "Policy"
    tag = "Tag"
    task = "Task"
    document = "Document"
    plugin = "Plugin"
    incident_priority = "IncidentPriority"
    incident_type = "IncidentType"
    incident = "Incident"

class EntityTypes(str, Enum):
    companytype = "CompanyTypes"
    userroletype = "UserRoleTypes"
    producttype = "ProductType"

class UserRoleTypes(str, Enum):
    user = "User"
    superuser = "SuperUser"
    admin = "Admin"
    staff = "Staff"
    owner = "Owner"
    anonymous = "Anonymous"