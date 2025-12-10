---
name: weather-info
description: Retrieve current weather conditions and forecast for a specified location. Provide information on temperature, precipitation, wind, and upcoming forecast. Use this skill when a user asks for the current weather or forecast for a specific city, zip code, or geographic location.
---

# Weather Information Skill

This skill allows you to retrieve real-time weather data and forecasts for a user-specified location. 

## When to Use This Skill

Invoke this skill whenever the user asks about:
- Current weather conditions for a location
- Weather forecast for a location
- Specific weather metrics like temperature, rain, snow, wind, etc. for a location

## Workflow

1. Determine the user's desired location
   - If provided, extract the city name, zip code, or geographic coordinates from the query
   - If no location specified, ask the user to provide a location
2. Call the weather API (see `scripts/get_weather.py`) with the location parameter
   - If API returns an error, inform the user the location was not found
3. Parse the API response JSON (see `references/api_response_format.md`) to extract:
   - Current conditions: temperature, precipitation, wind speed & direction, humidity 
   - Forecast: high/low temperatures, conditions, precipitation for next 5 days
4. Format the weather data into a human-readable response
   - Lead with current conditions 
   - Summarize the upcoming forecast
   - Use the templates in `references/response_templates.md`
5. Return the formatted weather report to the user

## Input Format

This skill expects the user to provide a location in their initial query. The location can be in any of these formats:
- City name: "Seattle"
- City, State/Country: "Paris, France"  
- Zip code: "90210"
- Geographic coordinates: "47.6062, -122.3321"

If no location is provided, follow up with the user to request a location before retrieving weather data.

## Output Format

The skill should return the weather information as a text response, using the following format:

Current conditions for {LOCATION}:
- Temperature: X °F / Y °C 
- Conditions: {sunny|cloudy|rain|snow}
- Precipitation: X inches
- Wind: X mph, direction

5-Day Forecast:
- Monday: High X °F / Low Y °F, {conditions} 
- Tuesday: High X °F / Low Y °F, {conditions}
- ...

See `references/response_templates.md` for more response formatting examples.

## Resources

- `scripts/get_weather.py`: Python script to call weather API with location parameter
- `references/api_response_format.md`: Documentation of expected JSON format returned by weather API
- `references/response_templates.md`: Example templates for formatting weather data into human-readable text

## Example Usage

User: What's the weather like in Seattle?
Assistant: *Uses skill to retrieve Seattle weather data and returns*:

Current conditions for Seattle, WA:  
- Temperature: 52°F / 11°C
- Conditions: Cloudy with showers 
- Precipitation: 0.4 inches
- Wind: 7 mph, NE

5-Day Forecast:
- Monday: High 54°F / Low 43°F, Rain likely
- Tuesday: High 50°F / Low 38°F, Showers
- Wednesday: High 48°F / Low 37°F, Mostly cloudy
- Thursday: High 51°F / Low 42°F, Chance of rain
- Friday: High 56°F / Low 44°F, Partly cloudy

Let me know if you need weather info for any other locations!

User: weather tomorrow in 90210