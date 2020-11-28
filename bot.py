import sys
import discord
from discord.ext import commands
import data

client = commands.Bot(command_prefix = '.')

'''

Things to work on -
1. Tell the user if they have not passed any argument
2. Date and time can be in past

'''

@client.event
async def on_ready():
    print("Bot is ready.")
    #print(type(client))

@client.command()
async def testing(ctx):
    data.checking_client(client, ctx.channel.id)

'''
command - reminder
Used to change the time(in minutes) before which everyone should receive an invite
'''
@client.command()
async def reminder(ctx, reminder):
    status = data.check_temp_meeting(ctx.channel.id)
    if not status:
        await ctx.send("No meeting in queue. Start a meeting then add offset")
        return
    if not data.check_valid_reminder(reminder):
        await ctx.send("Wrong format! - 1-99")
        return
    else:
        data.add_reminder_temp(ctx, reminder)

    check = data.check_allvalues_temp(ctx)
    if check == 2:
        await ctx.send("All values have been entered, use confirm to add the meeting")

'''
command - offset
Used to change the timezone (in +/- HH:MM) wrt UTC
'''
@client.command()
async def offset(ctx, offset_val):
    status = data.check_temp_meeting(ctx.channel.id)
    if not status:
        await ctx.send("No meeting in queue. Start a meeting then add offset")
        return
    if not data.check_valid_offset(offset_val):
        await ctx.send("Wrong format - +HH:MM or -HH:MM")
        return
    else:
        data.add_offset_temp(ctx, offset_val)

    check = data.check_allvalues_temp(ctx)
    if check == 2:
        await ctx.send("All values have been entered, use confirm to add the meeting")

'''
command - meeting
Used to start adding a meeting
'''
@client.command()
async def meeting(ctx, *name):
    #Check if a meeting is already there or not
    status = data.check_temp_meeting(ctx.channel.id)
    if status:
        await ctx.send("There is already a meeting in queue")
        await ctx.send(data.temp_values_remaining(ctx.channel.id))
        return
    if len(name) == 0:
        await ctx.send("Enter a valid name")
        return
    meeting_name = ' '.join(name)
    data.add_meeting_temp(ctx, meeting_name)
    await ctx.send("Meeting name has been added")

'''
command - location
Used to add a location to the meeting
'''
@client.command()
async def location(ctx, *location_name):
    status = data.check_temp_meeting(ctx.channel.id)
    if not status:
        await ctx.send("No meeting in queue. Start a meeting then add location")
        return
    
    if len(location_name) == 0:
        await ctx.send("Enter a valid location name")
        return
    location_name_string = ' '.join(location_name)
    data.add_location_temp(ctx, location_name_string)
    await ctx.send("Location has been added")
    
    check = data.check_allvalues_temp(ctx)
    if check == 1:
        await ctx.send("Offset is set to 0, use confirm command to add the meeting to the queue")
    elif check == 2:
        await ctx.send("All values have been entered, use confirm to add the meeting")

'''
command - time
Used to add a time to the meeting
'''
@client.command()
async def time(ctx, time_val):
    if not data.check_valid_time(time_val):
        await ctx.send("Valid format - HH:MM")
        return
    
    status = data.check_temp_meeting(ctx.channel.id)
    if not status:
        await ctx.send("No meeting in queue. Start a meeting then add time")
        return
    else:
        data.add_time_temp(ctx, time_val)
        await ctx.send("Time has been added")
    
    check = data.check_allvalues_temp(ctx)
    if check == 1:
        await ctx.send("Offset is set to 0, use confirm command to add the meeting to the queue")
    elif check == 2:
        await ctx.send("All values have been entered, use confirm to add the meeting")

'''
command - date
Used to add a date to the meeting
'''
@client.command()
async def date(ctx, date_val):
    if not data.check_valid_date(date_val):
        await ctx.send("Valid format - DD/MM/YYYY or DD.MM.YYYY or DD-MM-YYYY ")
        return
    status = data.check_temp_meeting(ctx.channel.id)
    if not status:
        await ctx.send("No meeting in queue. Start a meeting then add time")
    else:
        data.add_date_temp(ctx, date_val)
        await ctx.send("Date has been added")
    check = data.check_allvalues_temp(ctx)
    if check == 1:
        await ctx.send("Offset is set to 0, use confirm command to add the meeting to the queue")
    elif check == 2:
        await ctx.send("All values have been entered, use confirm to add the meeting")

'''
command - confirm
Used to add the meeting to final queue and to remind everyone
'''
@client.command()
async def confirm(ctx):
    status = data.check_temp_meeting(ctx.channel.id)
    if not status:
        await ctx.send("No meeting in queue. Add a meeting first")
        return
    check = data.check_allvalues_temp(ctx)
    if check == 0:
        await ctx.send("Fill all the fields first. Status of the meeting: ")
        await ctx.send(data.temp_values_remaining(ctx.channel.id))
        return
    else:
        #data.add_data_server(ctx.channel.id)
        await ctx.send(data.temp_values_remaining(ctx.channel.id))
        await ctx.send("Meeting has been added to the database")

'''
command - clear
Used to clear the chat
'''
@client.command()
async def clear(ctx):
    await ctx.channel.purge()
    #print(ctx.message.embeds)

'''
command - remind
Used to add users to the meeting
'''
@client.command()
async def remind(ctx):
    status = data.check_temp_meeting(ctx.channel.id)
    if not status:
        await ctx.send("No meeting in queue. Add a meeting first")
        return
    
    if len(ctx.message.mentions) == 0 and ctx.message.mention_everyone == False:
        await ctx.send("Mention valid users")
        return
    if ctx.message.mention_everyone == True:
        data.add_everyone_temp(ctx)
        await ctx.send("Everyone has been added")
    else :
        data.add_members_temp(ctx)
        await ctx.send("Users have been added")
    
    check = data.check_allvalues_temp(ctx)
    if check == 1:
        await ctx.send("Offset is set to 0, use confirm command to add the meeting to the queue")
    elif check == 2:
        await ctx.send("All values have been entered, use confirm to add the meeting")

'''
command - help
Used to display all the commands that are needed to add a meeting
'''
@client.command()
async def helper(ctx):
    await ctx.send("To add a meeting follow these steps -")
    await ctx.send("1. Use .meeting [Meeting Name] command to start adding a meeting")
    await ctx.send("2. Use .time [Time] command to add a time to the meeting")
    await ctx.send("3. Use .date [Date] command to add a date to the meeting")
    await ctx.send("4. Use .location [Location] command to add a location to the meeting")
    await ctx.send("5. (Optional) Use .offset to change the timezone from UTC +0:00 to your own local timezone")
    await ctx.send("6. (Optional) Use .reminder to change the reminder time from 10 mins")
    await ctx.send("7. Use .remind [@Member(s) / @everyone] to add members to the meeting")
    await ctx.send("8. Use .confirm to add the meeting")

client.run('NzE1MzA2NzkwMDE0NjgxMjAx.XtFmEQ.fSEPJ2Jv2BgTMRf7ay3ZIQry-ZQ')