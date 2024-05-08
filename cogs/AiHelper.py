import discord
from discord.ext import commands
from gradio_client import Client


class AiHelper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = Client("Qwen/CodeQwen1.5-7b-Chat-demo")



    @commands.slash_command(name="AIChat", description="Ask AI anything.")
    async def AIChat(self, ctx, *, query: str):
        await ctx.defer(ephemeral=True)

        try:
            numeric_query = int(query)
            query = str(numeric_query)
        except ValueError:
            pass

        result = self.client.predict(
            query=query,
            history=[],
            system="You are a helpful assistant.",
            api_name="/model_chat"
        )
        if result and result[1]:
            responses = result[1][0][1] if len(result[1][0]) > 1 else "No detailed response available."
            if len(responses) <= 2000:
                await ctx.followup.send(responses, ephemeral=True)
            else:
                max_length = 2000
                while responses:
                    slice_end = (responses[:max_length].rfind(' ') + 1) if ' ' in responses[:max_length] else max_length
                    to_send = responses[:slice_end].strip()
                    if to_send:
                        await ctx.followup.send(to_send, ephemeral=True)
                    responses = responses[slice_end:].strip()
        else:
            await ctx.followup.send("No response from API.", ephemeral=True)



def setup(bot):
    bot.add_cog(AiHelper(bot))
