from mongoengine import *
from datetime import datetime
import json
import database_host

connect(host = database_host.host)

class Meeting(EmbeddedDocument):
    meeting_name = StringField(required=True)
    time = StringField(required=True)
    date = StringField(required=True)
    offset = StringField(required=True)
    members_invited = ListField(IntField())
    location = StringField(required=True)
    reminder = IntField()
    unix_time = FloatField()

    def json(self):
        user_dict = {
            "meeting_name" : self.meeting_name,
            "time":self.time,
            "date":self.date,
            "offset":self.offset,
            "members_invited":self.members_invited,
            "location":self.location,
            "reminder":self.reminder,
            "unix_time":self.unix_time      
        }
        return json.dumps(user_dict)
    meta = {
        "indexes":["meeting_name"],
        "ordering":["-unix_time"]
    }


class Meeting_structure(Document):
    guild_id = IntField()
    guild_name = StringField(required=True)
    channel_id = IntField()
    channel_name = StringField(required = True)
    progress = BooleanField(default = False)
    meeting = EmbeddedDocumentField(Meeting)

    def json(self):
        user_dict = {
            "guild_id" : self.guild_id,
            "guild_name":self.guild_name,
            "channel_id":self.channel_id,
            "channel_name":self.channel_name,
            "progress":self.progress,
            # "meeting":self.meeting,
        }
        return json.dumps(user_dict)

    meta = {
        "indexes":["channel_id"],
        "ordering":["channel_id"]
    }

'''
Save a meeting
Get all meetings
Get one specific meeting
Delete one specific meeting
'''

def get_all_meetings():
    list_meetings = []
    all_meetings = Meeting_structure.objects()
    for i in all_meetings:
        temp_meeting = json.loads(i.json())
        temp_meeting_data = json.loads(i.meeting.json())
        temp_meeting.add("Meeting",temp_meeting_data)
        list_meetings.append(temp_meeting)
    return list_meetings


def save_meeting(meeting_data):
    meeting_dict = Meeting(
            meeting_name = meeting_data['Meeting']['meeting_name'],
            time = meeting_data['Meeting']['time'],
            date = meeting_data['Meeting']['date'],
            offset = meeting_data['Meeting']['offset'],
            members_invited = meeting_data['Meeting']['members_invited'],
            location = meeting_data['Meeting']['location'],
            reminder = meeting_data['Meeting']['reminder'],
            unix_time = meeting_data['Meeting']['unix_time']      
        )
    Meeting_structure(
        guild_id = meeting_data['guild_id'],
        guild_name = meeting_data['guild_name'],
        channel_id = meeting_data['channel_id'],
        channel_name = meeting_data['channel_name'],
        progress = meeting_data['progress'],
        meeting = meeting_dict,
        ).save()

def delete_meeting(meeting_data):
    meeting_dict = Meeting(
            meeting_name = meeting_data['Meeting']['meeting_name'],
            time = meeting_data['Meeting']['time'],
            date = meeting_data['Meeting']['date'],
            offset = meeting_data['Meeting']['offset'],
            members_invited = meeting_data['Meeting']['members_invited'],
            location = meeting_data['Meeting']['location'],
            reminder = meeting_data['Meeting']['reminder'],
            unix_time = meeting_data['Meeting']['unix_time']      
        )
    Meeting_structure(
        guild_id = meeting_data['guild_id'],
        guild_name = meeting_data['guild_name'],
        channel_id = meeting_data['channel_id'],
        channel_name = meeting_data['channel_name'],
        progress = meeting_data['progress'],
        meeting = meeting_dict,
        ).delete()

'''
meeting_dict = Meeting(
            meeting_name = "Checking",
            time="12:23",
            date="24/03/2021",
            offset="0:00",
            members_invited=[123,456],
            location="Discord",
            reminder=10,
            unix_time=1234.12      
        )
Meeting_structure(
    guild_id = 234,
    guild_name = "BICO",
    channel_id = 1234,
    channel_name = "Commands",
    progress = True,
    meeting = meeting_dict,
    ).save()

print("Done")
temp = Meeting_structure.objects(meeting = meeting_dict).get()
print(temp.meeting.json())
'''