import json
import os
import re
import subprocess
from pyrogram import Client
from pyrogram.types import Message
from services.humanFunctions import humanBitrate, humanSize, remove_N


async def tgInfo(client: Client, msg: Message):
    print("Processing Telegram file...", flush=True)
    message = msg.reply_to_message

    if not message or not message.media:
        raise Exception("`This message does not contain any supported media.`")

    # Determine media type
    mediaType = message.media.value
    if mediaType == 'video':
        media = message.video
    elif mediaType == 'audio':
        media = message.audio
    elif mediaType == 'document':
        media = message.document
    else:
        print("This media type is not supported", flush=True)
        raise Exception("`This media type is not supported`")

    # Extract file details
    mime = media.mime_type
    fileName = media.file_name
    size = media.file_size

    print(fileName, size, flush=True)

    # Validate document type
    if mediaType == 'document' and all(x not in mime for x in ['video', 'audio', 'image']):
        print("Makes no sense", flush=True)
        raise Exception("`This file makes no sense to me.`")

    # Download or stream the file
    if int(size) <= 50_000_000:  # 50 MB limit
        await message.download(file_name=fileName)
    else:
        async for chunk in client.stream_media(message, limit=5):
            with open(fileName, 'ab') as f:
                f.write(chunk)

    try:
        # Run mediainfo commands
        mediainfo = subprocess.check_output(['mediainfo', fileName]).decode("utf-8")
        mediainfo_json = json.loads(
            subprocess.check_output(['mediainfo', fileName, '--Output=JSON']).decode("utf-8")
        )

        # Human-readable size
        readable_size = humanSize(size)

        # Update mediainfo details
        lines = mediainfo.splitlines()
        if 'image' not in mime:
            duration = float(mediainfo_json['media']['track'][0]['Duration'])
            bitrate_kbps = (size * 8) / (duration * 1000)
            bitrate = humanBitrate(bitrate_kbps)

            for i in range(len(lines)):
                if 'File size' in lines[i]:
                    lines[i] = re.sub(r": .+", f': {readable_size}', lines[i])
                elif 'Overall bit rate' in lines[i] and 'Overall bit rate mode' not in lines[i]:
                    lines[i] = re.sub(r": .+", f': {bitrate}', lines[i])
                elif 'IsTruncated' in lines[i] or 'FileExtension_Invalid' in lines[i]:
                    lines[i] = ''

            remove_N(lines)

        # Save updated mediainfo to a file
        txt_file = f'{fileName}.txt'
        with open(txt_file, 'w') as f:
            f.write('\n'.join(lines))

        # Send the file back as a document
        await msg.reply_document(document=txt_file, caption=f'`{fileName}`')

        print("Telegram file Mediainfo sent", flush=True)

    except Exception as e:
        await message.reply_text("Something bad occurred particularly with this file.")
        print(f"Error processing file: {e}", flush=True)

    finally:
        # Cleanup
        if os.path.exists(fileName):
            os.remove(fileName)
        if os.path.exists(txt_file):
            os.remove(txt_file)


print("Telegram file module loaded", flush=True)
