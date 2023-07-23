import os
import random
import discord


from datetime import datetime
from discord import File
from discord.ext import commands
from dotenv import load_dotenv
from PIL import Image, ImageFont
from easy_pil import Editor, load_image_async, Font
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


intents = discord.Intents.all()
bot = commands.Bot(command_prefix='.', intents=intents)


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    discord_id = Column(Integer, primary_key=True)
    discord_name = Column(String)
    discriminator = Column(String)
    avatar_url = Column(String)
    status = Column(String)
    rule_confirmation = Column(Boolean)
    joined_at = Column(String)


class Channel(Base):
    __tablename__ = 'channel'
    channel_id = Column(Integer, primary_key=True)
    channel_name = Column(String)
    created_at = Column(String)
    channel_type = Column(String)


class Rule_Data(Base):
    __tablename__ = 'rule_data'
    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer)
    rule_name = Column(String)


class GuildEntryLog(Base):
    __tablename__ = 'guild_entry_log'
    id = Column(Integer, primary_key=True, autoincrement=True)
    discord_id = Column(Integer, ForeignKey('user.discord_id'))
    entry_dateTime = Column(String)


class GuildExitLog(Base):
    __tablename__ = 'guild_exit_log'
    id = Column(Integer, primary_key=True, autoincrement=True)
    discord_id = Column(Integer, ForeignKey('user.discord_id'))
    exit_dateTime = Column(DateTime)


class Tickets(Base):
    __tablename__ = 'tickets'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_number = Column(Integer)
    discord_id = Column(Integer, ForeignKey('user.discord_id'))
    status = Column(String)
    created_at = Column(DateTime, default=datetime.now)


engine = create_engine('sqlite:///database.db', echo=False)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


####
# TICKET NUMBERS

ticket_numbers = set(range(1000, 100001))

####


#####
# BOT COMMANDS
#####


@bot.command()
async def setchannel(ctx, greeting):

    greeting_channel = ctx.channel.id
    session = Session()

    try:
        if greeting.lower() == "welcome":

            # CHECK IF WELCOME CHANNEL ALREADY EXITS
            greeting_check = session.query(Channel).filter(
                Channel.channel_type == "greeting - welcome").first()

            if greeting_check:
                await ctx.channel.send('There is already a Welcome channel set. Please use "/unsetchannel welcome" then reissue this command again.')

            else:
                session.query(Channel).filter(Channel.channel_id == greeting_channel).update(
                    {Channel.channel_type: "greeting - welcome"}, synchronize_session=False)

                session.commit()

                response = 'This has been set as the "Welcome" channel'
                await ctx.channel.send(response)

        elif greeting.lower() == "goodbye":

            # CHECK IF GOODBYE CHANNEL EXISTS
            greeting_check = session.query(Channel).filter(
                Channel.channel_type == "greeting - goodbye").first()

            if greeting_check:
                await ctx.channel.send('There is already a Goodbye channel set. Please use "/unsetchannel goodbye" then reissue this command again.')

            else:
                session.query(Channel).filter(Channel.channel_id == greeting_channel).update(
                    {Channel.channel_type: "greeting - goodbye"}, synchronize_session=False)

                session.commit()

                response = 'This has been set as the "Goodbye" channel'

                await ctx.channel.send(response)

    except ValueError:

        response = 'Please use ".setchannel welcome" or ".setchannel goodbye"'
        await ctx.channel.send(response)

    finally:
        session.close()


@bot.command()
async def unsetchannel(ctx, greeting):

    try:
        session = Session()

        if greeting.lower() == "welcome":

            greeting_channel = session.query(Channel).filter(
                Channel.channel_type == "greeting - welcome").first()

            if greeting_channel:

                greeting_channel.channel_type = None
                session.commit()

                await ctx.channel.send("The Welcome channel has been unset")
                await ctx.channel.send(f'WARNING! {ctx.author.mention} You currently do not have a Welcome channel set.')
                await ctx.channel.send('Use ".setchannel welcome" in any channel you want to set as the Welcome channel.')

            else:
                await ctx.channel.send("There is currently no Welcome channel set")
                await ctx.channel.send('Use ".setchannel welcome" in any channel you want to set as the Welcome channel.')

        elif greeting.lower() == "goodbye":

            greeting_channel = session.query(Channel).filter(
                Channel.channel_type == "greeting - goodbye").first()

            if greeting_channel:

                greeting_channel.channel_type = None
                session.commit()

                await ctx.channel.send("The Goodbye channel has been unset")
                await ctx.channel.send(f'WARNING! {ctx.author.mention} You currently do not have a Goodbye channel set.')
                await ctx.channel.send('Use ".setchannel goodbye" in any channel you want to set as the Goodbye channel.')

            else:
                await ctx.channel.send("There is currently no Goodbye channel set")
                await ctx.channel.send('Use ".setchannel goodbye" in any channel you want to set as the Goodbye channel.')

    except ValueError:
        response = 'Please use ".unsetchannel welcome" or ".unsetchannel goodbye"'
        await ctx.channel.send(response)

    finally:
        session.close()

    session.close()


@bot.command()
async def setrules(ctx):

    # DEFINE INDIVIDUAL RULES
    rules = {
        "discord_rules": discord.Embed(title="DISCORD RULES",
                                       description="**1.** Please change your server nickname to include your faction’s credentials and your gamertag example as follows: (OFW) Mrs_Forbid\n\n**2.** Be respectful in all channels any bullying, disrespect, discrimination, sexism and/or racism etc will NOT be tolerated and will result in an immediate ban\n\n**3.** DO NOT pm staff members please use the dedicated requests channel and a staff member will respond as timely as possible\n\n**4.** DO NOT @everyone @here unnecessarily unless given express permission from a moderator or your in a channel that allows such mentions ie ⁠тяα∂є-яєqυєѕтѕ\n\n**5.** NO spamming and NO unsolicited / unsafe links\n\n**6.** Be respectful in all voice channels no screaming, arguing with people, abuse or excessive background noise etc. may result in you being moved or muted for the duration of the call",
                                       color=0xf54900).set_footer(text="Oceania Faction Wars"),
        "game_rules": discord.Embed(title="IN-GAME RULES (SERVER RULES)",
                                    description="**Do you have a moment of time for our lord and savior? ALL HAIL LORD CLANG**\n\n**1. **NO glitching or exploits ie glitching through voxels to scout an enemy base \n\n**2.** When pistons,rotors and hinges are not in use they must be turned off! Failing to do so may result in your grid being deleted if it affects the servers health \n\n**3.** Name all grids in your ownership or they may be deleted in the monthly trash clean up (grids can be named from a control seat/control panel) \n\n**4.** Factions are capped at a 4 member limit this will increase as server population increases\n\n**5.** please do not construct lag machines to tank the server health or gain an unfair advantage during combat such machines will be deleted without warning\n\n**6.** Attacking a faction outside of war is a crime against humanity see below section for warfare rules and rules of engagement this may result in hangars/ships being deleted, warnings and or bans at staff decisions\n\n**7.** Space stations and asteroid bases must be within 150km of a planet/moon any grids further out may be deleted if not moved **",
                                    color=0xf54900).set_footer(text="Oceania Faction Wars"),
        "warfare_rules": discord.Embed(title="WARFARE AND TERMS OF ENGAGEMENT",
                                       description="**(PMW) PLAYER MADE WEAPONS**\n\n**TURRETS (PMW Turrets are weapons connected to a parent grid through rotors, hinges, or pistons, and are controlled via script or remote control)**\n\n**1.** More than one PMW cannot be fired manually by pilot/character at a time\n\n**2.** No more than 16 total fixed weapons per PMW turret\n\n**3.** No more than 10 total PMW turrets per large grid\n\n**4.** No more than 3 total PMW turrets per small grid\n\n**5.** PMW turrets must have a beacon/antenna turned on while in use and it’s broadcast set to the turrets firing range\n\n**MISSILES (PMW Missiles are disposable self-propelled impact/explosive devices controlled via script or remote control)**\n\n**1.** All Missiles must be named and left as small/large grid\n\n**2.** A maximum of 4 decoy blocks can be used per missile\n\n**3.** NO lotus style missiles\n\n**4.** PMW missiles must have a beacon/antenna turned and it’s broadcast set to maximum range\n\n**PVP RULES**\n\n**1.** NO Combat logging doing so is surrendering your grid and loot it may also result in warnings at staff discretion\n\n**2.** If you are going to raid another player / declare war on them you must have a base somewhere within the server limits that can be counter raided\n\n**3.** Points of Interest (POI) are warzones until they have been claimed (an antenna turned and renamed to factions credentials) some POI need to be fully reconstructed before they can be claimed\n\n**4.** Do not fire unless fired upon ie -this means if your turrets are left on and they engage with something then it is presumed that the target can fire back to disable the threat\n\n**5.** When engaged in battle broadcasting of any communications onboard must be left on\n\n**6.** Once a faction surrenders during battle an immediate ceasefire must occur from all involved in the fight the faction that surrenders must allow the enemy to board and loot however the grid is to remain intact /control of the surrendering faction\n\n**TERMS OF WAR**\n\n**1.** Going to war with another faction takes favour for unrestricted combat both factions must both mutually agree to go to war using using ⁠Oceania Faction Wars⁠ωαя-яєqυєѕтѕ\n\n**2.** Should a faction wish to make a peace deal both factions involved in the war must mutually agree to peace using ⁠Oceania Faction Wars⁠ωαя-яєqυєѕтѕ (should a faction make peace there will be a 15 day grace period before the same factions can go to war again)\n\n**3.** If Party A and Party B engage in war, it is expected that Party A's allies will join Party A, and Party B's allies will join Party B. Failure to do so will result in the alliance between Party A and Party B being broken\n\n**4.** PMW Rules still apply in war as does **NO COMBAT LOGGING**\n\n**5.** A base raid must only consist of 6 respawns each faction member once all 6 respawns have been used any remaining grids/characters must be retreated from battle immediately there will be a 6 hour grace period once a raid has been completed or failed before another raid from any faction can commence",
                                       color=0xf54900).set_footer(text="Oceania Faction Wars"),
        "confirmation": discord.Embed(title="Please react to this message to agree to the discord rules and gain access to the rest of the server 💗",
                                      color=0x11f27d).set_footer(text="Oceania Faction Wars")
    }

    # DELETE COMMAND SENT
    await ctx.message.delete()

    # OPEN SESSION TO THE DATABASE
    session = Session()

    rules_check = session.query(Channel).filter(
        Channel.channel_type == "rules").first()

    if rules_check:
        rules_check.channel_type = None
        session.commit()

    session.query(Channel).filter(Channel.channel_id == (ctx.channel.id)).update(
        {Channel.channel_type: "rules"}, synchronize_session=False)

    session.commit()

    # SEND EACH RULE IN AN INDIVIDUAL MESSAGE
    await ctx.channel.send(embed=rules["discord_rules"])

    await ctx.channel.send("\n\n---------------\n\n")

    await ctx.channel.send(embed=rules["game_rules"])

    await ctx.channel.send("\n\n---------------\n\n")

    await ctx.channel.send(embed=rules["warfare_rules"])

    await ctx.channel.send("\n\n---------------\n\n")

    # SEND CONFIRMATION MESSAGE AND STORES MESSADE ID
    discord_rules_message = await ctx.channel.send(embed=rules["confirmation"])
    discord_rules_message_id = discord_rules_message.id

    rule_data = session.query(Rule_Data).filter(
        Rule_Data.rule_name == "confirmation").first()
    rule_data.message_id = discord_rules_message_id

    session.commit()

    session.close()


@bot.command()
async def tickets(ctx):
    await ctx.message.delete()

    ticket_message = {
        "tickets": discord.Embed(title="TICKETS!",
                                 description="Please react below to open a new ticket\n📩",
                                 color=0x00b0f4).set_footer(text="Oceania Faction Wars")
    }

    session = Session()

    # CHECK IF TICKET RULE DATA EXISTS
    rule_data_check = session.query(Rule_Data).filter(
        Rule_Data.rule_name == "tickets").first()

    if not rule_data_check:

        tickets_rule_data_entry = Rule_Data(message_id=None,
                                            rule_name="tickets"
                                            )
        session.add(tickets_rule_data_entry)
        session.commit()

    ticket_check = session.query(Channel).filter(
        Channel.channel_type == "tickets").first()

    if ticket_check:
        ticket_check.channel_type = None
        session.commit()

    session.query(Channel).filter(Channel.channel_id == ctx.channel.id).update(
        {Channel.channel_type: "tickets"}, synchronize_session=False)

    # SEND TICKET MESSAGE AND STORES MESSADE ID
    tickets_message = await ctx.channel.send(embed=ticket_message["tickets"])
    tickets_message_id = tickets_message.id

    tickets_rule_data = session.query(Rule_Data).filter(
        Rule_Data.rule_name == "tickets").first()

    tickets_rule_data.message_id = tickets_message_id

    session.commit()
    session.close()


@bot.command()
async def announce(ctx, title: str, *, body: str):
    await ctx.message.delete()
    embed = discord.Embed(title=title, description=body, color=0x00ff00)
    embed.set_author(name="Announcement")
    embed.set_footer(text="Oceania Faction Wars")
    await ctx.send(embed=embed)

#####
# END COMMANDS
#####


@bot.event
async def on_ready():

    # CONFIRMS THE BOT HAS BEEN STARTED
    print(f'{bot.user} has succesfully logged in!')

    # OPEN SESSION TO THE DATABASE
    session = Session()

    # DISPLAYS THE GUILDS THE BOT IS JOINED ON
    print("We are connected to the following guilds ~")

    for guild in bot.guilds:
        print(guild.name)

        # GRAB ALL CHANNELS
        for channel in guild.channels:

            channel_check = session.query(Channel).filter(
                Channel.channel_id == int(channel.id)).first()

            if channel_check:
                return

            channel_entry = Channel(channel_id=int((channel.id)),
                                    channel_name=str((channel.name)),
                                    created_at=str((channel.created_at)))

            session.add(channel_entry)
            session.commit()

        # INSERT MEMBERS INTO user TABLE
        for member in guild.members:

            user_check = session.query(User).filter(
                User.discord_id == int(member.id)).first()

            if user_check:

                return

            if member.avatar is not None:
                member_avatar_url = member.avatar.url
            else:
                member_avatar_url = None

            user_entry = User(discord_id=int(member.id),
                              discord_name=str((member.name)),
                              discriminator=str((member.discriminator)),
                              avatar_url=str(member_avatar_url),
                              status="Active",
                              rule_confirmation=False,
                              joined_at=str((member.joined_at)))

            session.add(user_entry)
            session.commit()

    rule_data = session.query(Rule_Data).filter(
        Rule_Data.rule_name == "confirmation").first()

    if not rule_data:
        rule_entry = Rule_Data(message_id=None,
                               rule_name="confirmation")
        session.add(rule_entry)
        session.commit()

    else:
        return

    session.close()


@bot.event
async def on_member_join(member):

    # OPEN SESSION TO THE DATABASE
    session = Session()

    # CHECK IF USER EXISTS IN USER TABLE
    user_check = session.query(User).filter(
        User.discord_id == int(member.id)).first()

    # CHECK IF THEY HAVE AN AVATAR
    if not user_check:
        if member.avatar is not None:
            member_avatar_url = member.avatar.url
        else:
            member_avatar_url = None

        # ADD USER
        user_entry = User(discord_id=int(member.id),
                          discord_name=str((member.name)),
                          discriminator=str((member.discriminator)),
                          avatar_url=str(member_avatar_url),
                          status="Active",
                          rule_confirmation=False,
                          joined_at=str((member.joined_at)))
        session.add(user_entry)
        session.commit()

    # FIND THE ESTABLISHED WELCOME CHANNEL
    welcome_channel = session.query(Channel).filter(
        Channel.channel_type == "greeting - welcome").first()

    # ESTABLISH CHANNEL AS THE "WELCOME" CHANNEL
    channel = bot.get_channel(int(welcome_channel.channel_id))

    user_entry = GuildEntryLog(discord_id=int((member.id)),
                               entry_dateTime=str((member.joined_at)))

    session.add(user_entry)
    session.commit()
    session.close()

# CREATE IMAGE TO SERVE A WELCOME MESSAGE

    # SELECT RANDOM BACKGROUND IMAGE
    background_image_path = random.choice(
        [os.path.join('backgrounds', fn) for fn in os.listdir('backgrounds')])
    background = Editor(background_image_path)

    # CHECK IF MEMBER HAS AN AVATAR OR NOT
    if member.avatar is None:
        profile_image = Image.open("no_avatar.jpg")
    else:
        profile_image = await load_image_async(str(member.avatar.url))

    # RESIZE IMAGE AND CIRCULARIZE
    profile = Editor(profile_image).resize((150, 150)).circle_image()

    # DEFINE FONTS
    # poppins = Font.poppins(size=40, variant="bold")
    poppins_medium = Font.poppins(size=30, variant="bold")
    poppins_small = Font.poppins(size=35, variant="light")

    researcher = ImageFont.truetype(
        font="fonts/researcher-researcher-squid-700.ttf", size=30)

# BEGIN LAYERING IMAGE

    # LAYER BACKGROUND
    background.paste(profile, (325, 90))

    # LAYER AVATAR
    background.ellipse((325, 90), 150, 150, outline="white", stroke_width=5)

    # LAYER TEXT
    background.text(
        (400, 260), "WELCOME TO", color="white", font=poppins_medium, align="center")

    # LAYER TEXT
    background.text(
        (400, 300), f"{member.guild.name}", color="white", font=researcher, align="center")

    # LAYER TEXT
    background.text((400, 350), f"{member.name}#{member.discriminator}",
                    color="white", font=poppins_small, align="center")

    # CREATE THE IMAGE/FILE
    file = File(fp=background.image_bytes, filename="welcome.jpg")

    await channel.send(f"Hello {member.mention}! Do you have a moment of time for our lord and savior? **__ALL HAIL LORD CLANG__**")
    # await channel.send(f"Hello {member.mention}! Welcome to **{member.guild.name}**.")
    await channel.send(file=file)
    await channel.send("Please read the <#1122607459425595533> to gain access to this server.")


@bot.event
async def on_member_remove(member):

    goodbye_messages = [lambda member_name, member_discriminator: f"Farewell, **{member_name}#{member_discriminator}**, as you venture beyond the cosmic horizon!",
                        lambda member_name, member_discriminator: f"**{member_name}#{member_discriminator}** has embarked on a celestial journey, bidding adieu to our stellar realm.",
                        lambda member_name, member_discriminator: f"The cosmic winds carry **{member_name}#{member_discriminator}** away, leaving our astral domain behind.",
                        lambda member_name, member_discriminator: f"As the stardust settles, **{member_name}#{member_discriminator}** departs from our celestial expanse, leaving us in awe.",
                        lambda member_name, member_discriminator: f"**{member_name}#{member_discriminator}**'s departure from our galactic realm marks the beginning of a new interstellar chapter.",
                        lambda member_name, member_discriminator: f"In the vast expanse of space, **{member_name}#{member_discriminator}** ventures forth, leaving our stellar system behind.",
                        lambda member_name, member_discriminator: f"As **{member_name}#{member_discriminator}** vanishes into the infinite abyss, our celestial sphere bids them farewell.",
                        lambda member_name, member_discriminator: f"**{member_name}#{member_discriminator}**'s departure sends ripples of farewell across our astral plane.",
                        lambda member_name, member_discriminator: f"With bittersweet emotions, our stellar cluster watches **{member_name}#{member_discriminator}** vanish into the great unknown.",
                        lambda member_name, member_discriminator: f"**{member_name}#{member_discriminator}** embarks on a cosmic odyssey, leaving our celestial boundaries to explore the uncharted realms.",
                        lambda member_name, member_discriminator: f"Farewell, **{member_name}#{member_discriminator}**, may your journey through the cosmos be filled with wonders beyond imagination.",
                        lambda member_name, member_discriminator: f"As **{member_name}#{member_discriminator}** sails into the cosmic sea, our celestial domain shines brighter in their honor.",
                        lambda member_name, member_discriminator: f"The universe beckons, and **{member_name}#{member_discriminator}** answers the call, departing our stellar domain.",
                        lambda member_name, member_discriminator: f"**{member_name}#{member_discriminator}** slips away from our astral realm, leaving behind a trail of stardust and memories.",
                        lambda member_name, member_discriminator: f"As **{member_name}#{member_discriminator}** fades into the stellar distance, our celestial sphere wishes them safe travels.",
                        lambda member_name, member_discriminator: f"**{member_name}#{member_discriminator}** takes a leap into the vastness of space, bidding farewell to our stellar expanse.",
                        lambda member_name, member_discriminator: f"In the cosmic dance, **{member_name}#{member_discriminator}**'s departure from our astral plane adds a new rhythm to the universe.",
                        lambda member_name, member_discriminator: f"**{member_name}#{member_discriminator}**'s departure leaves a void in our celestial sphere, reminding us of their extraordinary presence.",
                        lambda member_name, member_discriminator: f"Beyond the boundaries of our galactic system, **{member_name}#{member_discriminator}** sets off on an interstellar adventure.",
                        lambda member_name, member_discriminator: f"As **{member_name}#{member_discriminator}** leaves our cosmic realm, the cosmos awaits their incredible journey to unfold.",
                        ]
    session = Session()

    # FIND THE ESTABLISHED GOODBYE CHANNEL
    goodbye_channel = session.query(Channel).filter(
        Channel.channel_type == "greeting - goodbye").first()

    # ESTABLISH CHANNEL AS THE "GOODBYE" CHANNEL
    channel = bot.get_channel(int(goodbye_channel.channel_id))

    date = datetime.now()
    user_entry = GuildExitLog(discord_id=int((member.id)),
                              exit_dateTime=date)

    session.add(user_entry)
    session.commit()
    session.close()

    goodbye_message = random.choice(goodbye_messages)(
        member.name, member.discriminator)

    await channel.send(goodbye_message)


@bot.event
async def on_reaction_add(reaction, user):

    session = Session()

    # CHECK IF REACTION HAPPENED IN RULES CHANNEL
    rule_channel = session.query(Channel).filter(
        Channel.channel_type == "rules").first()

    tickets_channel = session.query(Channel).filter(
        Channel.channel_type == "tickets").first()

    if reaction.message.channel.id == rule_channel.channel_id:

        # CHECK IS REACTION HAPPENED ON RULE MESSAGE
        rule_message = session.query(Rule_Data).filter(
            Rule_Data.message_id == (reaction.message.id)).first()

        if rule_message:

            # UPDATE USER TABLE WITH RULE_CONFIRMATION

            session.query(User).filter(User.discord_id == (user.id)).update(
                {User.rule_confirmation: True}, synchronize_session=False)

            session.commit()
            session.close()

            # GIVE USER ENGINEER ROLE
            guild = bot.get_guild(1122294005028376636)
            engineer_role_id = 1122670071576272906
            engineer_role = guild.get_role(engineer_role_id)

            if engineer_role:
                await user.add_roles(engineer_role)
                print(f"{user.name} has claimed the Engineer role.")
            else:
                print("Engineer Role Not Found.")

    if reaction.message.channel.id == tickets_channel.channel_id:

        # CHECK IF REACTION HAPPENED ON TICKET MESSAGE
        ticket_message = session.query(Rule_Data).filter(
            Rule_Data.rule_name == "tickets").first()

        if reaction.message.id == ticket_message.message_id:

            new_ticket_number = "ticket-" + random.sample(ticket_numbers, 1)[0]
            ticket_numbers.remove(new_ticket_number)

            # CREATE DATABASE ENTRY
            new_ticket = Tickets(ticket_number=new_ticket_number,
                                 discord_id=str(user.id),
                                 status="Active"
                                 )
            session.add(new_ticket)
            session.commit()

            # CREATE A NEW TICKET CHANNEL


@bot.event
async def on_guild_channel_create(channel):
    session = Session()

    channel_entry = Channel(channel_id=int((channel.id)),
                            channel_name=str((channel.name)),
                            created_at=str((channel.created_at)))
    session.add(channel_entry)
    session.commit()
    session.close()

bot.run(TOKEN)
