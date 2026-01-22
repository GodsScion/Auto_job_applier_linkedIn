# Directive: People Messaging

## Goal
Send personalized messages to LinkedIn connections and people you may know to build professional network.

## Inputs
- **Config**: `config/recruiter_messaging.py` for limits and delays (reuse settings).
- **AI Client**: For generating personalized messages.
- **Connection List**: List of people to message (could be from search or manual input).
- **User Information**: Personal details for message personalization.

## Tools
- `execution/messaging_utility.py`: Standalone script for messaging workflows.

## Instructions
1. **Check Configuration**: Verify messaging is enabled and not in messaging-only mode for job applications.
2. **Collect Targets**: Identify people to message (connections, search results).
3. **Generate Messages**: Use AI to create personalized messages for each target.
4. **Send Messages**: Execute messaging with proper delays and error handling.
5. **Track Results**: Log all activities to dedicated CSV log.
6. **Respect Limits**: Implement delays and daily limits to avoid detection.

## Edge Cases
- **Connection Limits**: LinkedIn limits weekly connection requests.
- **Message Templates**: Fallback to generic templates if AI fails.
- **Profile Privacy**: Skip profiles that don't accept messages.
- **Duplicate Prevention**: Check if already messaged recently.

## Outputs
- **Messages Sent**: Count of successful messages.
- **CSV Log**: History in `all excels/people_messages_history.csv`.
- **Console Logs**: Monitoring and debug information.