import random
import time
from pytrends.request import TrendReq

# Function to generate real-time keywords based on user input (industry, objective, location)
def generate_keywords(industry, objective, location):
    pytrends = TrendReq(hl='en-US', tz=360)

    # Retry mechanism
    retries = 2
    while retries > 0:
        try:
            # Get real-time trending keywords related to the industry and objective
            pytrends.build_payload([industry, objective], cat=0, timeframe='now 1-d', geo=location, gprop='')

            # Fetch related trending keywords
            related_queries = pytrends.related_queries()

            # Check if the data structure is as expected
            industry_trends = related_queries.get(industry, {}).get('top', [])
            objective_trends = related_queries.get(objective, {}).get('top', [])

            # Log the results for debugging
            print(f"Related queries for {industry}: {industry_trends}")
            print(f"Related queries for {objective}: {objective_trends}")

            # If no trends, log the issue and continue
            if not industry_trends:
                print(f"No trends found for industry: {industry}")
            if not objective_trends:
                print(f"No trends found for objective: {objective}")
            
            break  # Exit loop if request is successful

        except Exception as e:
            print(f"Error fetching related queries: {str(e)}")
            retries -= 1
            print(f"Retrying... ({3 - retries} retries left)")
            time.sleep(2)  # Sleep for 2 seconds before retrying

    if retries == 0:
        print("Failed to fetch trends after multiple retries.")
        industry_trends = []
        objective_trends = []

    # Refine keywords based on fetched trends
    industry_keywords = [
        f"{industry} trends {location}", f"{industry} growth in {location}",
        f"top {industry} opportunities in {location}", f"best {industry} services in {location}"
    ]
    objective_keywords = [
        f"{objective} strategies for {industry}", f"{objective} optimization in {industry}",
        f"successful {objective} for {industry}", f"boosting {objective} in {industry}"
    ]

    # Combine industry and objective-based keywords with real-time trends
    trending_keywords = [trend['query'] for trend in industry_trends + objective_trends]

    if trending_keywords:
        print(f"Trending Keywords: {trending_keywords}")
    else:
        print("No trending keywords found.")

    # Final list of keywords combining static and real-time data
    keywords = industry_keywords + objective_keywords + trending_keywords
    if trending_keywords:
        keywords.extend(random.sample(trending_keywords, 3))  # Add 3 random trending keywords for variety

    return keywords
