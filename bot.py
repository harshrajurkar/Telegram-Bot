from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from utils.keyword_generator import generate_keywords
from utils.trends_scraper import fetch_ppc_trends
from utils.faq_ai import get_ai_response
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

# /start command with inline buttons
async def start(update, context):
    keyboard = [
        [
            InlineKeyboardButton("Start Analysis", callback_data='analyze'),
            InlineKeyboardButton("Get PPC Trends", callback_data='trends')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome! Use the buttons below to start or ask a question:",
        reply_markup=reply_markup
    )

# /menu command to ask for options (Start, Trends, Keywords, Help)
async def handle_menu_command(update, context):
    keyboard = [
        [
            InlineKeyboardButton("Start", callback_data='start'),
            InlineKeyboardButton("Help", callback_data='help')
        ],
        [
            InlineKeyboardButton("PPC Trends", callback_data='trends'),
            InlineKeyboardButton("Generate Keywords", callback_data='generate_keywords')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Please choose one of the following options:",
        reply_markup=reply_markup
    )

# /analyze command with a prompt to ask questions
async def analyze(update, context):
    context.user_data['step'] = 'industry'
    await update.message.reply_text("What industry is your business in?")

# Handle user text input based on step
async def text_handler(update, context):
    step = context.user_data.get('step')
    user_input = update.message.text.strip()

    if step == 'industry':
        if not user_input:
            await update.message.reply_text("Industry cannot be empty. Please provide a valid input.")
            return
        context.user_data['industry'] = user_input
        await update.message.reply_text("What is your business objective?")
        context.user_data['step'] = 'objective'

    elif step == 'objective':
        if not user_input:
            await update.message.reply_text("Objective cannot be empty. Please provide a valid input.")
            return
        context.user_data['objective'] = user_input
        await update.message.reply_text("Do you have a website? Please select:", reply_markup=website_buttons())
        context.user_data['step'] = 'website'

    elif step == 'website_url':
        if not user_input.startswith('http'):
            await update.message.reply_text("Please provide a valid URL starting with http or https.")
            return
        context.user_data['website_url'] = user_input
        await update.message.reply_text("Do you have any social media platforms? Please select:", reply_markup=social_media_buttons())
        context.user_data['step'] = 'social_media'

    elif step == 'social_media_url':
        if not user_input.startswith('http'):
            await update.message.reply_text("Please provide valid social media URL(s) starting with http or https.")
            return
        context.user_data['social_media_url'] = user_input
        await update.message.reply_text("Do you use PPC campaigns? Please select:", reply_markup=ppc_buttons())
        context.user_data['step'] = 'ppc_campaigns'

    elif step == 'ppc_permission':
        if user_input.lower() not in ['yes', 'no']:
            await update.message.reply_text("Please reply with 'Yes' or 'No'.")
            return
        context.user_data['ppc_permission'] = user_input
        await update.message.reply_text("Who are you trying to reach? Please select:", reply_markup=audience_buttons())
        context.user_data['step'] = 'target_audience'

    elif step == 'target_audience':
        if not user_input:
            await update.message.reply_text("Target audience cannot be empty. Please provide a valid input.")
            return
        context.user_data['target_audience'] = user_input
        await update.message.reply_text("Select the location(s) you'd like to target:", reply_markup=location_buttons())
        context.user_data['step'] = 'location'

    elif step == 'location':
        if not user_input:
            await update.message.reply_text("Location cannot be empty. Please provide a valid input.")
            return
        context.user_data['location'] = user_input
        await update.message.reply_text("Generating keywords...")
        try:
            keywords = generate_keywords(
                context.user_data['industry'], context.user_data['objective'], context.user_data['location']
            )
            await update.message.reply_text(f"Generated Keywords: {', '.join(keywords)}")
        except ValueError as e:
            await update.message.reply_text(f"Error: {str(e)}")
        context.user_data['step'] = None
    else:
        await update.message.reply_text("I didn't understand that. Type /analyze to start again.")

# Buttons for Website Selection (Yes/No)
def website_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Yes", callback_data='website_yes')],
        [InlineKeyboardButton("No", callback_data='website_no')]
    ])

# Buttons for Social Media Selection (Yes/No)
def social_media_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Yes", callback_data='social_media_yes')],
        [InlineKeyboardButton("No", callback_data='social_media_no')]
    ])

# Buttons for PPC Campaign Selection (Yes/No)
def ppc_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Yes", callback_data='ppc_yes')],
        [InlineKeyboardButton("No", callback_data='ppc_no')]
    ])

# Buttons for Target Audience Selection
def audience_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Young Adults", callback_data='audience_young_adults')],
        [InlineKeyboardButton("Professionals", callback_data='audience_professionals')],
        [InlineKeyboardButton("Parents", callback_data='audience_parents')]
    ])

# Buttons for Location Selection
def location_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("USA", callback_data='location_usa')],
        [InlineKeyboardButton("India", callback_data='location_india')],
        [InlineKeyboardButton("UK", callback_data='location_uk')],
        [InlineKeyboardButton("Australia", callback_data='location_australia')]
    ])

# /trends command (fetch PPC trends)
async def trends(update, context):
    try:
        trends = fetch_ppc_trends()  # Call the function from trend_scraper
        if trends:
            trend_text = "\n".join(trends)
            await update.message.reply_text(f"Latest PPC Trends:\n{trend_text}")
        else:
            await update.message.reply_text("No trends available at the moment. Please try again later.")
    except Exception as e:
        await update.message.reply_text(f"Error fetching trends: {str(e)}")

# Handle FAQ (AI-powered responses)
async def faq(update, context):
    question = update.message.text.strip()
    if not question:
        await update.message.reply_text("Please ask a valid question.")
        return
    try:
        answer = get_ai_response(question)
        await update.message.reply_text(answer)
    except Exception as e:
        await update.message.reply_text(f"Error fetching answer: {str(e)}")

# Handle button press callback
async def button_handler(update, context):
    query = update.callback_query
    await query.answer()  # Acknowledge the button press

    if query.data == 'start':
        await query.message.reply_text("Welcome! Use the buttons below to start or ask a question:")
        await start(update, context)

    elif query.data == 'help':
        await faq(update, context)

    elif query.data == 'trends':
        await trends(update, context)

    elif query.data == 'generate_keywords':
        await query.message.reply_text("Please follow the steps to generate your keywords.")

    elif query.data == 'analyze':
        await query.message.reply_text("What industry is your business in?")
        context.user_data['step'] = 'industry'

    elif query.data == 'website_yes':
        context.user_data['website'] = 'Yes'
        await query.message.reply_text("Please provide the website URL.")
        context.user_data['step'] = 'website_url'

    elif query.data == 'website_no':
        context.user_data['website'] = 'No'
        await query.message.reply_text("Do you have any social media platforms? Please select:", reply_markup=social_media_buttons())
        context.user_data['step'] = 'social_media'

    elif query.data == 'social_media_yes':
        context.user_data['social_media'] = 'Yes'
        await query.message.reply_text("Please provide the social media URL(s).")
        context.user_data['step'] = 'social_media_url'
    elif query.data == 'social_media_no':
        context.user_data['social_media'] = 'No'
        await query.message.reply_text("Do you use PPC campaigns? Please select:", reply_markup=ppc_buttons())
        context.user_data['step'] = 'ppc_campaigns'

    elif query.data == 'ppc_yes':
        context.user_data['ppc_campaigns'] = 'Yes'
        await query.message.reply_text("Please provide permission to analyze your PPC campaign data.")
        context.user_data['step'] = 'ppc_permission'
    elif query.data == 'ppc_no':
        context.user_data['ppc_campaigns'] = 'No'
        await query.message.reply_text("Who are you trying to reach? Please select:", reply_markup=audience_buttons())
        context.user_data['step'] = 'target_audience'

    elif query.data.startswith('audience_'):
        audience = query.data.split('_')[1]  # Extract audience from callback data
        context.user_data['target_audience'] = audience
        await query.message.reply_text("Select the location(s) you'd like to target:", reply_markup=location_buttons())
        context.user_data['step'] = 'location'

    elif query.data.startswith('location_'):
        location = query.data.split('_')[1]  # Extract location from callback data
        context.user_data['location'] = location
        await query.message.reply_text("Generating keywords...")
        try:
            keywords = generate_keywords(
                context.user_data['industry'], context.user_data['objective'], context.user_data['location']
            )
            await query.message.reply_text(f"Generated Keywords: {', '.join(keywords)}")
        except ValueError as e:
            await query.message.reply_text(f"Error: {str(e)}")
        context.user_data['step'] = None

# Main function to run the bot
def main():
    application = Application.builder().token(TELEGRAM_API_TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", handle_menu_command))
    application.add_handler(CommandHandler("help", faq))
    application.add_handler(CommandHandler("trends", trends))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    application.add_handler(CallbackQueryHandler(button_handler))

    # Start polling
    application.run_polling()

if __name__ == "__main__":
    main()
