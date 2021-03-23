import sys
import discord
from discord.ext import commands
import data
from discord_key import bot_key

# Prefix used in discord to send a command
client = commands.Bot(command_prefix = '.')

# Removing the default help command so that we can set our own
client.remove_command('help')
'''
TO DO

1.  Add support for firebase
'''

# When the bot is ready
@client.event
async def on_ready():
    data.basic_setup()
    print("Bot is ready.")


'''
command - reminder
Used to change the time(in minutes) before which everyone should receive an invite
'''
@client.command()
async def reminder(ctx, *reminder):
    # To check if there is a meting in the queue from this specific channel
    # Returns true or false
    status = data.check_temp_meeting(ctx.channel.id)
    
    if status is False:
        await ctx.send("No meeting in queue. Start a meeting then add offset")
        return
    # Checks if the format of the string enetered is correct or not
    if data.check_valid_reminder(" ".join(reminder)) is False:
        await ctx.send("Wrong format! - 1-99")
        return
    else:
        # Adds the reminder time to the meeting information
        data.add_reminder_temp(ctx, " ".join(reminder))

    check = data.check_allvalues_temp(ctx)
    if check == 2:
        await ctx.send("All values have been entered, use confirm to add the meeting")

'''
command - offset
Used to change the timezone (in +/- HH:MM) wrt UTC
'''
@client.command()
async def offset(ctx, *offset_val):
    # Basic data checking
    status = data.check_temp_meeting(ctx.channel.id)
    if status is False:
        await ctx.send("No meeting in queue. Start a meeting then add offset")
        return
    if data.check_valid_offset(" ".join(offset_val)) is False:
        await ctx.send("Wrong format - +HH:MM or -HH:MM")
        return
    else:
        # Adds the timezone offset to the meeting information
        data.add_offset_temp(ctx, " ".join(offset_val))

    check = data.check_allvalues_temp(ctx)
    if check == 2:
        await ctx.send("All values have been entered, use confirm to add the meeting")

'''
command - meeting
Used to start adding a meeting
'''
@client.command()
async def meeting(ctx, *name):
    # Basic data checking
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
    # Basic data checking
    status = data.check_temp_meeting(ctx.channel.id)
    if status is False:
        await ctx.send("No meeting in queue. Start a meeting then add location")
        return
    
    if len(location_name) == 0:
        await ctx.send("Enter a valid location name")
        return
    # Adds the location name to the meeting information
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
async def time(ctx, *time_val):
    # Basic data checking
    if data.check_valid_time(" ".join(time_val)) is False:
        await ctx.send("Valid format - HH:MM")
        return
    
    status = data.check_temp_meeting(ctx.channel.id)
    if status is False:
        await ctx.send("No meeting in queue. Start a meeting then add time")
        return
    else:
        data.add_time_temp(ctx, " ".join(time_val))
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
async def date(ctx, *date_val):
    # Basic data checking
    if data.check_valid_date(" ".join(date_val)) is False:
        # Checks the format of the entered string
        await ctx.send("Valid format - DD/MM/YYYY or DD.MM.YYYY or DD-MM-YYYY ")
        return
    status = data.check_temp_meeting(ctx.channel.id)
    if status is False:
        await ctx.send("No meeting in queue. Start a meeting then add time")
    else:
        # Adds the data to the queue
        data.add_date_temp(ctx, " ".join(date_val))
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
    if status is False:
        await ctx.send("No meeting in queue. Add a meeting first")
        return
    check = data.check_allvalues_temp(ctx)
    if check == 0:
        await ctx.send("Fill all the fields first. Status of the meeting: ")
        await ctx.send(data.temp_values_remaining(ctx.channel.id))
        return
    else:
        #Check for correct date time.
        isValidDateTime = data.check_valid_datetime(ctx.channel.id)    
        if isValidDateTime is True:
            
            #Call the final save funtion
            await ctx.send(data.temp_values_remaining(ctx.channel.id))
            data.save_data(ctx.channel.id, client)
            await ctx.send("Meeting has been added to the database")
        
        else:
            await ctx.send("The date time is in past. Please update it.")

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
    # Basic data checking
    status = data.check_temp_meeting(ctx.channel.id)
    if status is False:
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
async def help(ctx):
    await ctx.send("To add a meeting follow these steps- \n \
    1. Use .meeting [Meeting Name] command to start adding a meeting \n \
    2. Use .time [Time] command to add a time to the meeting Valid format - HH:MM \n \
    3. Use .date [Date] command to add a date to the meeting Valid format - DD/MM/YYYY or DD.MM.YYYY or DD-MM-YYYY \n \
    4. Use .location [Location] command to add a location to the meeting \n \
    5. Use .remind [[@]Member(s) / [@]everyone] to add members to the meeting \n \
    6. (Optional) Use .offset to change the timezone from UTC +0:00 to your own local timezon Valid format - HH:M \n \
    7. (Optional) Use .reminder to change the reminder time from 10 min \n \
    8. Use .confirm to add the meeting")

'''
@client.command()
async def start(ctx):
    #await data.checking_client(client,ctx.channel.id)
    pass
'''
client.run(bot_key)
