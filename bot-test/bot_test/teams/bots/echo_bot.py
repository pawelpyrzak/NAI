# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.core import ActivityHandler, MessageFactory, TurnContext
from botbuilder.schema import ChannelAccount


class EchoBot(ActivityHandler):

    async def on_members_added_activity(
        self, members_added: [ChannelAccount], turn_context: TurnContext
    ):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Hello and welcome!")


    async def on_message_activity(self, turn_context: TurnContext):

        if turn_context.activity.text.lower().strip() == "!hello":
            # Send a hello message back to the user
            await turn_context.send_activity("Hello!")

        await turn_context.send_activity(
            MessageFactory.text(f"Echo: {turn_context.activity.text}")
        )
        channel_id = turn_context.activity.conversation.id
        channel_data = turn_context.activity.channel_data
        channel_name = channel_data.get("team", {}).get("name", "Unknown Channel")
        print(f"Channel Name: {channel_name}")
        print(f"Channel ID: {channel_id}")
