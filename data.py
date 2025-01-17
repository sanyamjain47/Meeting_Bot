import re
import threading
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime
from apscheduler.schedulers import asyncio
import time as time_lib

data_temp = list()
data_queue = list()
scheduled_meetings = asyncio.AsyncIOScheduler()


def basic_setup():
    scheduled_meetings.start()

    #Get all the queued meetings from the server
    # Queue the meetings
'''
Adds the temp_meeting to the firebase server
'''
def add_data_server(channel_id):
    data_to_add = temp_values_remaining(channel_id)
    
    # Use a service account
    cred = credentials.Certificate('serviceAccount.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()

    #To add channel_id to channel list
    doc_ref = db.collection(u'Channels').document(u'List')
    data_server_guilds_list = doc_ref.get()
    data_server_guilds_list = data_server_guilds_list.to_dict()

    if data_server_guilds_list is None:
        data_server_guilds_list = {'all_channels':[str(channel_id)]}
        doc_ref.set(data_server_guilds_list)
    
    elif channel_id not in data_server_guilds_list['all_channels']:
        data_server_guilds_list['all_channels'].append(channel_id)
        doc_ref.set(data_server_guilds_list)
    

    data_meeting_ref = db.collection(str(channel_id)).document('Data')
    data_meeting = data_meeting_ref.get()
    data_meeting = data_meeting.to_dict()

    #If the meeting is not there, add it and start a thread to add it
    if data_meeting is None:
        data_meeting = {
            'meetings':[data_to_add]
        }
        data_meeting_ref.set(data_meeting)

    if data_meeting['meetings'] is None or data_to_add not in data_meeting['meetings']:
        data_meeting['meetings'].append(data_to_add)
        data_meeting_ref.set(data_meeting)
        # Start a thread

'''
Adds how much time before the meeting the notification needs to be sent
'''
def add_reminder_temp(ctx, time):
    for i in data_temp:
        if i['channel_id'] == ctx.channel.id:
            i['Meeting']['reminder'] = time

'''
Adds the offset (Timezone difference) to the meeting
'''
def add_offset_temp(ctx, offset):
    for i in data_temp:
        if i['channel_id'] == ctx.channel.id:
            i['Meeting']['offset'] = offset

'''
Adds the location to the meeting
'''
def add_location_temp(ctx, location):
    for i in data_temp:
        if i['channel_id'] == ctx.channel.id:
            i['Meeting']['location'] = location

'''
Adds the date to the meeting
'''
def add_date_temp(ctx, date):
    for i in data_temp:
        if i['channel_id'] == ctx.channel.id:
            i['Meeting']['date'] = date

'''
Adds the time to the meeting
'''
def add_time_temp(ctx, time):
    for i in data_temp:
        if i['channel_id'] == ctx.channel.id:
            i['Meeting']['time'] = time

'''
Adds everyone to the meeting
'''
def add_everyone_temp(ctx):

    members_list = ctx.channel.members
    members_list.append(ctx.message.author)
    members_list_id = []

    for i in members_list:
        if i.bot != True:
            members_list_id.append(i.id)
    
    for i in data_temp:
        if i['channel_id'] == ctx.channel.id:
            i['Meeting']['members_invited'] = members_list_id.copy()


'''
Adds the mentioned members to the meeting
'''
def add_members_temp(ctx):
    members_list = ctx.message.mentions
    members_list.append(ctx.message.author)
    
    members_list_id = []
    for i in members_list:
        if i.bot != True:
            members_list_id.append(i.id)
        
    for i in data_temp:
        if i['channel_id'] == ctx.channel.id:
            i['Meeting']['members_invited'] = members_list_id.copy()

'''
Adds the meeting to a temp
'''
def add_meeting_temp(ctx, meeting_name):
    guild_id = ctx.guild.id
    guild_name = ctx.guild.name
    channel_id = ctx.channel.id
    channel_name = ctx.channel.name
    progress = True

    to_add = {
        'guild_id' : guild_id,
        'guild_name' : guild_name,
        'channel_id' : channel_id,
        'channel_name' : channel_name,
        'progress' : progress,
        'Meeting' : {
            'meeting_name' : meeting_name,
            'time': None,
            'date': None,
            'offset': 0,
            'members_invited': None,
            'location': None,
            'reminder':10,
            'unix_time':0
        }
    }
    data_temp.append(to_add)

'''
Checks if there is a meeting that needs to be added - in progress of filling
'''
def check_temp_meeting(channel_id):
    status = False
    for i in data_temp:
        if i['channel_id'] == channel_id:
            status = i['progress']
    
    return status

'''
Checks if the time entered is valid
'''
def check_valid_time(time):
    pattern = '^([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$'
    result = re.match(pattern, time)
    return result
    

'''
Checks if the offset entered is valid
'''
def check_valid_offset(offset):
    pattern = '^[+,-]([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$'
    result = re.match(pattern, offset)
    return result

'''
Checks if the date entered is valid
'''
def check_valid_date(date):
    pattern = r'^(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(\/|-|\.)(?:0?[1,3-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)0?2\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})$'
    result = re.match(pattern, date)
    return result


'''
Checks if the date and time are not in past
'''
def check_valid_datetime(channel_id):
    system_offset = -time_lib.timezone

    meeting_temp = temp_values_remaining(channel_id)
    time = meeting_temp['time']
    date = meeting_temp['date']
    offset = meeting_temp['offset']
    
    offset_seconds = datetime.strptime(offset[1:], "%H:%M")
    offset_seconds = (offset_seconds - datetime(1900, 1, 1)).total_seconds()
    
    if(offset[0] == '-'):
        offset_seconds = -1*offset_seconds
    
    if "/" in date:
        datetime_obj = datetime.strptime(date + " " + time, "%d/%m/%Y %H:%M")
    
    elif "-" in date:
        datetime_obj = datetime.strptime(date + " " + time, "%d-%m-%Y %H:%M")
    
    else:
        datetime_obj = datetime.strptime(date + " " + time, "%d.%m.%Y %H:%M")
    
    
    datetime_seconds = datetime.timestamp(datetime_obj)
    user_time = datetime_seconds-offset_seconds+system_offset
    current_time = datetime.now().timestamp()
    time_difference = user_time - current_time
    time_difference = time_difference/60
    
    if time_difference < int(meeting_temp['reminder']) :
        return False
    else:
        update_time(user_time - int(meeting_temp['reminder']*60), channel_id)
        return True

'''
Checks if the reminder time entered is valid
'''
def check_valid_reminder(time):
    pattern = r'^[0-9]?[1-9]$'
    result = re.match(pattern, time)
    return result

'''
Returns the dictionary of meeting with the values filled
'''
def temp_values_remaining(channel_id):
    status = {}
    for i in data_temp:
        if i['channel_id'] == channel_id:
            status = i['Meeting']
    
    return status

'''
Checks if all the values have been entered
'''
def check_allvalues_temp(ctx):
    temp = {}
    for i in data_temp:
        if i['guild_id'] == ctx.guild.id:
            temp = i['Meeting']
    check = [temp['time'], temp['date'], temp['members_invited'], temp['location']]
    if None in check:
        return 0
    elif temp['offset'] == 0:
        return 1
    else:
        return 2

def update_time(unix_time, channel_id):
    for i in data_temp:
        if i['channel_id'] == channel_id:
            i['Meeting']['unix_time'] = unix_time
            return


def save_data(channel_id,client):
    #Shift meeting of channel_id from data_temp to data_queue
    
    for i in data_temp:
        if i['channel_id'] == channel_id:
            i['progress'] = False
            data_queue.append(i)
            data_temp.remove(i)
            ## Add this meeting toz the queue server
            schedule_reminder(i,client)
            break
            
def schedule_reminder(values, client):
    scheduled_meetings.add_job(send_reminder, args = [client,values],trigger = "date",\
        run_date = datetime.fromtimestamp(values['Meeting']['unix_time']))


'''
async def checking_client(client, channel_id):
    print(type(client.get_channel(channel_id)))
    for i in data_temp:
        for member in i['Meeting']['members_invited']:
            #print(client.get_user(member))
            await client.get_user(member).send("CHeck")
'''
async def send_reminder(client, values):
    for member in values['Meeting']['members_invited']:
        await client.get_user(member).send("Formatted message here")
    data_queue.remove(values)