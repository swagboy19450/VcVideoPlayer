import os
import asyncio
from pytgcalls import idle
from pytgcalls import PyTgCalls
from pytgcalls import StreamType
from pytgcalls.types.input_stream import AudioParameters
from pytgcalls.types.input_stream import InputAudioStream
from pytgcalls.types.input_stream import InputVideoStream
from pytgcalls.types.input_stream import VideoParameters
from pyrogram import Client, filters
from pyrogram.types import Message
from config import API_ID, API_HASH, SESSION_NAME

app = Client(SESSION_NAME, API_ID, API_HASH)
call_py = PyTgCalls(app)

@Client.on_message(filters.command("stream"))
async def stream(client, m: Message):
    replied = m.reply_to_message
    if not replied:
        await m.reply("`Reply to some Video!`")
   
    elif replied.video or replied.document:
        msg = await m.reply("`Downloading...`")
        video = await client.download_media(m.reply_to_message)
        chat_id = m.chat.id
        await msg.edit("`Processing...`")
        os.system("ffmpeg -i f'{video}' -f s16le -ac 1 -ar 48000 f'audio{chat_id}.raw' -f rawvideo -r 20 -pix_fmt yuv420p -vf scale=640:-1 f'video{chat_id}.raw'")
        try:
            await call_py.start()
            audio_file = f'audio{chat_id}.raw'
            video_file = f'video{chat_id}.raw'
            while not os.path.exists(audio_file) or \
                    not os.path.exists(video_file):
                time.sleep(0.125)
            await call_py.join_group_call(
                chat_id,
                InputAudioStream(
                    audio_file,
                    AudioParameters(
                        bitrate=48000,
                    ),
                ),
                InputVideoStream(
                    video_file,
                    VideoParameters(
                        width=640,
                        height=360,
                        frame_rate=20,
                    ),
                ),
                stream_type=StreamType().local_stream,
            )
            await idle()
        except Exception as e:
            await msg.edit(f"**Error** -- `{e}`")
    else:
        await m.reply("`Reply to some Video!`")

@Client.on_message(filters.command("stopstream"))
async def stopvideo(client, m: Message):
    chat_id = m.chat.id
    try:
        await call_py.start()
        await call_py.leave_group_call(chat_id)
        await m.reply("**⏹️ Stopped Streaming!**")
        await idle()
    except Exception as e:
        await m.reply(f"**🚫 Error** - `{e}`")
