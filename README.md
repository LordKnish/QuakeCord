# Quakecord

A discord bot that retrieves and displays information about recent earthquakes from the European Mediterranean Seismological Centre (EMSC).

## Table of Contents

- [Program](#program)
- [Data Source](#data-source)
- [Libraries Used](#libraries-used)
- [Instructions](#instructions)
- [Future Development](#future-development)

## Program

Quakecord is a discord bot that provides information about recent earthquakes to users in a Discord server. It retrieves the information from the European Mediterranean Seismological Centre (EMSC) and displays it in a user-friendly format.

## Data Source

The data used by Quakecord is sourced from the European Mediterranean Seismological Centre (EMSC). The EMSC is a leading provider of real-time earthquake information and has a vast database of earthquake data.

## Libraries Used

Quakecord uses the following libraries:

- Requests
- Discord.py
- Folium

## Instructions

1. Clone this repository to your local machine.
2. Create a virtual environment and activate it.
3. Install the required libraries using `pip install -r requirements.txt`.
4. Create a bot in Discord's Developer Portal and get its token.
5. Add the bot to your Discord server.
6. In the `quakecord.py` file, replace `TOKEN` with your bot's token.
7. Run the `quakecord.py` file to start the bot.

## Future Development

- Ability to notify users of earthquakes that meet certain criteria.
- More detailed historical information, including graphs and maps.
- Adding more data sources for earthquake information.
- Improving the visual representation of the information provided by the bot.

## Contributing

We welcome contributions from the open-source community. If you would like to contribute to Quakecord, please follow these guidelines:

1. Fork the repository
2. Create a branch for your changes (e.g. `feature/new-feature` or `bugfix/fix-error`)
3. Commit your changes with descriptive commit messages
4. Push your changes to your forked repository
5. Create a pull request to the main repository with a clear explanation of your changes and the problem they solve.

## License

Quakecord is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.
