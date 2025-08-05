**Module 1 \- Emotional Monitoring**

| ID | Description | Priority |
| ----- | ----- | ----- |
| FR2.1.1 | When the system is powered on and operational, the system shall continuously monitor for user presence and environmental readiness to initiate emotion sensing. | High |
| FR2.1.2 | At fixed intervals or when user presence is detected, the system shall retrieve available data from body vital sign inputs, onboard camera, and microphone channels. | High |
| FR2.1.3 | Upon data retrieval, the system shall preprocess the inputs (e.g., normalize heart rate, extract facial features, generate speech transcript) for further emotion classification. | High |
| FR2.1.4 | For each input type (biometric, facial, speech/music), the system shall apply a pre-trained emotion detection model to infer the user’s emotional state and label it with a confidence score. | High |
| FR2.1.5 | After individual emotion predictions are obtained, the system shall combine the results using a fusion logic to compute a final emotional state, considering source confidence and availability. | High |
| FR2.1.6 | The system shall store the detected emotion, confidence score, contributing sources, and timestamp into the user’s emotion history for future retrieval. | High |
| FR2.1.7 | If any input source (e.g., camera, microphone, or wearable) is temporarily unavailable, the system should continue monitoring using the remaining input sources and log the degraded monitoring state. | Medium |
| FR2.1.8 | When a previously unavailable input source becomes available again, the system shall automatically resume full multimodal emotion monitoring. | Medium |
| FR2.1.9 | If all input sources become unavailable, the system shall suspend emotion monitoring, inform the user of the issue, and log the failure event. | High |


**Module 2 \- Wellness Engagement** 

| ID | Description | Priority |
| ----- | ----- | ----- |
| FR2.2.1 | When the user calls the Well-Bot’s wake word or a scheduled check-in is triggered, the system shall activate and provide audio and visual confirmation of readiness via speaker and display. | High |
| FR2.2.2 | If the user provides verbal input indicating a wellness-related need, the system shall analyze the intent and offer a wellness activity suggestion based on user history or predefined preferences. | High |
| FR2.2.3 | If the user accepts the suggested activity or explicitly requests a supported activity, the system shall initiate the selected wellness activity module. | High |
| FRs of extended Wellness Engagement activities can be referred from the remaining tables |  |  |
| FR2.2.4 | Upon completing an activity, the system shall store any user responses, content, and interaction logs with a timestamp in the user’s wellness history. | High |
| FR2.2.5 | If the user terminates an activity before completion, the system shall erase any incomplete activity logs and notify the user that the session has ended. | Medium |
| FR2.2.6 | After an activity concludes (completed or cancelled), the system should ask the user if they require further assistance and listen for verbal input. | Medium |
| FR2.2.7 | If the user provides unclear input during activity selection or while engaging, the system shall prompt the user to clarify or repeat their response. | High |
| FR2.2.8 | If an activity module fails to load or is unavailable, the system shall notify the user of the issue, log the fallback event, and may suggest an alternative available activity. | High |


**Module 2.1 \- Converse with Context Awareness**

| ID | Description | Priority |
| ----- | ----- | ----- |
| FR2.2.1.1 | When the Wellness Engagement activity is initiated, the system shall provide visual and audio confirmation of readiness via the droid’s screen and speaker. | High |
| FR2.2.1.2 | When the user speaks, the system shall begin recording audio input, and transcribe the user’s speech. | High |
| FR2.2.1.3 | Upon successful transcription, the system shall combine the transcript with relevant information from past conversations to produce an augment prompt, and pass it to a Large Language Model (LLM) to generate a response . | High |
| FR2.2.1.4 | The system shall deliver the generated response verbally together with a visually synchronized facial expression on the Well-Bot’s display. | High |
| FR2.2.1.5 | After delivering a response, the system shall wait for a user reply;  If the user provides a valid reply, the system shall resume the response loop. | High |
| FR2.2.1.6 | If no reply is detected, the system should prompt the user to continue the conversation, up to 3 times. | Medium |
| FR2.2.1.7 | If the user does not respond after 3 prompts, the system shall end the conversation and log the session closure. | Medium |
| FR2.2.1.8 | If the user explicitly gives a termination command (e.g., “end conversation”), the system shall acknowledge the user command and immediately end the session and store the final state. | High |
| FR2.2.1.9 | If speech recording or transcription fails, the system shall notify the user and retry before terminating the session and logging the failure. | High |
| FR2.2.1.10 | If the transcribed input is unclear (e.g., due to background noise or mumbled speech), the system shall prompt the user to repeat their message more clearly. | High |
| FR2.2.1.11 | The system should store all completed transcripts, response history, and timestamps into the conversation log for future personalization purposes. | Medium |


**Module 2.2 \- Voice and Photo Journaling**

| ID | Description | Priority |
| ----- | ----- | ----- |
| FR2.2.2.1 | When the Wellness Engagement activity is initiated, the system shall provide visual and audio confirmation of readiness via the droid’s screen and speaker. | High |
| FR2.2.2.2 | When the user begins speaking, the system shall record the voice input until a predefined stopping phrase (e.g., "I'm done") is detected. | High |
| FR2.2.2.3 | After recording is completed, the system shall prompt the user via audio to ask whether they want to attach a photo to the journal entry; if the user agrees, the system shall activate the onboard camera and capture a photo, else continue. | Medium |
| FR2.2.2.4 | The system shall save the transcribed text, photo (if applicable), with a timestamp as the journal entry. | High |
| FR2.2.2.5 | The saved journal entry shall be stored to the database and should appear on the user’s web dashboard interface. | High |
| FR2.2.2.6 | If recording or transcription fails, the system shall inform the user, log the error, and prompt them to try recording again. | High |
| FR2.2.2.7 | If camera capture fails during the photo prompt, the system shall notify the user and continue to save the journal entry without the image. | Medium |
| FR2.2.2.8 | The system should store all final logs (text, photo metadata, timestamps) in an indexed format to support future dashboard retrieval and sorting. | Medium |


**Module 2.3 \- Guided Meditation and Breathing Exercise with Calming Music**

| ID | Description | Priority |
| ----- | ----- | ----- |
| FR2.2.3.1 | When the Wellness Engagement activity is initiated, the system shall provide visual and audio confirmation of readiness via the droid’s screen and speaker. | High |
| FR2.2.3.2 | At the start of the activity, the system shall prompt the user to select a meditation theme from the list of available pre-recorded sessions. | High |
| FR2.2.3.3 | If the selected meditation theme is available, the system shall confirm the user's choice and provide audio-visual feedback indicating the session is about to begin. | High |
| FR2.2.3.4 | If the selected theme is not available, the system shall inform the user, log the unavailability, and prompt the user to select another available theme. | High |
| FR2.2.3.5 | After confirming theme availability, the system shall stream or play the corresponding pre-recorded meditation guide with calming background music. | High |
| FR2.2.3.6 | During the session, the user may interrupt by voice; if an interruption is detected, the system shall prompt the user to confirm if they wish to terminate the session early. | Medium |
| FR2.2.3.7 | If the user confirms early termination, the system shall stop playback and end the session; if the user declines, the system shall resume the session from the interruption point. | Medium |
| FR2.2.3.8 | Upon successful completion of the meditation guide, the system should offer follow-up wellness features or allow the user to exit. | Medium |
| FR2.2.3.9 | If audio playback fails during the session, the system shall notify the user of the issue and log the failure event. | High |
| FR2.2.3.10 | If the selected audio file cannot be loaded, the system shall apologize to the user and return to the theme selection step. | High |


**Module 2.4 \- Make a Gratitude List** 

| ID | Description | Priority |
| ----- | ----- | ----- |
| FR2.2.4.1 | When the Wellness Engagement activity is initiated, the system shall provide visual and audio confirmation of readiness via the droid’s screen and speaker. | High |
| FR2.2.4.2 | The system shall record and transcribe spoken gratitude statements in real-time. | High |
| FR2.2.4.3 | The system shall detect when the user has finished speaking using command “I’m done”. | High |
| FR2.2.4.4 | After a set number of gratitude statements, the system shall offer a follow-up reflective prompt. | Medium |
| FR2.2.4.5 | The system shall compile and timestamp all transcribed input from the session into one complete gratitude entry. | High |
| FR2.2.4.6 | The system shall ensure the entry is saved to the user’s web-based dashboard for future access. | High |
| FR2.2.4.7 | If the backend is unreachable, the system shall cache the entry locally and attempt to sync once connectivity is restored. | High |
| FR2.2.4.8 | If transcription fails during the session, the system shall prompt the user to repeat their input (up to 3 times). After 3 failed transcription attempts, the system shall skip saving for that session and log the failure. | High |
| FR2.2.4.9 | The system shall allow the user to skip the reflection prompt without disrupting the saving of initial gratitude statements. | Medium |


**Module 2.5 \- Spiritual Quote of the Day with Reflection Questions**

| ID | Description | Priority |
| ----- | ----- | ----- |
| FR2.2.5.1 | When the Wellness Engagement activity is initiated, the system shall provide visual and audio confirmation of readiness via the droid’s screen and speaker. | High |
| FR2.2.5.2 | The system shall automatically trigger the spiritual quote feature at a scheduled daily time. | High |
| FR2.2.5.3 | The system shall retrieve a spiritual or motivational quote from a pre-curated database. | High |
| FR2.2.5.4 | The system shall filter and select the quote based on the user’s selected cultural or spiritual background. | High |
| FR2.2.5.5 | The system shall narrate the quote to the user. | High |
| FR2.2.5.6 | After presenting the quote, the system shall retrieve and follow up with a reflection question related to the quote. | High |
| FR2.2.5.7 | The system shall listen for a verbal response from the user after asking the reflection question. | Medium |
| FR2.2.5.8 | The system shall allow the user to respond with a request for another quote. | Medium |
| FR2.2.5.9 | If no response is received after a timeout period, the system shall gracefully end the session with a polite closing. | Medium |
| FR2.2.5.10 | If the quote database is inaccessible, the system shall notify the user of the failure and prompt to try again later. | High |
| FR2.2.5.11 | If the TTS or display module is unavailable, the system shall inform the user and skip the current cycle. | High |
| FR2.2.5.12 | The system shall display an appropriate facial expression on the Well-Bot’s screen throughout the entire spiritual quote and reflection session to enhance empathetic delivery. | Medium |


**Module 2.6 \- Make a To-Do List**

| ID | Description | Priority |
| ----- | ----- | ----- |
| FR2.2.6.1 | When the Wellness Engagement activity is initiated, the system shall provide visual and audio confirmation of readiness via the droid’s screen and speaker. | High |
| FR2.2.6.2 | Upon activation, the system shall prompt the user to begin listing their tasks. | High |
| FR2.2.6.3 | The system shall record and transcribe the user's spoken input using a speech-to-text module. | High |
| FR2.2.6.4 | The system shall segment transcribed input into individual task items based on natural language understanding. | High |
| FR2.2.6.5 | The system shall detect when the user has finished speaking using command “I’m done”. | High |
| FR2.2.6.6 | Once input ends, the system shall compile and timestamp the segmented task items into a structured to-do list format. | High |
| FR2.2.6.7 | The system shall ensure the entry is saved to the user’s web-based dashboard for future access. | High |
| FR2.2.6.8 | The to-do list shall be made accessible and editable via the user’s web dashboard. | Medium |
| FR2.2.6.9 | If the backend is unreachable, the system shall cache the entry locally and attempt to sync it when the connection is restored. | Medium |
| FR2.2.6.10 | If transcription fails, the system shall prompt the user to retry. If transcription fails 3 times consecutively, the system shall skip saving the entry and log the session as failed. | Medium |

**Module 3 \- Entertainment**

| ID | Description | Priority |
| ----- | ----- | ----- |
| FR2.3.1 | When the user calls the wake word, the system shall activate and provide visual and audio confirmation of readiness to interact. | High |
| FR2.3.2 | Upon receiving user speech input, the system shall analyze the transcript for entertainment-related intents (e.g., dance along with song, joke, story) using a predefined intent classifier. | High |
| FR2.3.3 | If an entertainment is inferred or explicitly requested, the system shall offer a list of available entertainment or initiate a relevant activity directly based on user preference or historical usage. | High |
| FR2.3.4 | During an entertainment activity, the system shall guide the user through the selected activity using voice-based prompts and feedback. | High |
| FR2.3.5 | Upon completion of the entertainment activity, the system should store any user responses, audio logs, or activity metadata (e.g., type, timestamp) in the user's entertainment history. | Medium |
| FR2.3.6 | If the user terminates the activity prematurely or declines to continue, the system should log this action and return to an idle state without storing partial responses. | Medium |
| FR2.3.7 | If a requested entertainment activity is unavailable (e.g., due to module failure), the system shall inform the user and may suggest an alternative activity if available. | High |
| FR2.3.8 | If the user’s input is unclear or contains unrecognized commands, the system shall prompt the user to repeat the input clearly or choose from suggested options. | High |
| FR2.3.9 | If multiple entertainment features are available after an activity ends, the system should offer follow-up support or allow the user to return to the main entertainment menu. | Medium |


**Module 3.1 \- Tell a Funny Joke**

| ID | Description | Priority |
| ----- | ----- | ----- |
| FR2.3.1.1 | When the Entertainment activity is initiated, the system shall provide visual and audio confirmation of readiness via the droid’s screen and speaker. | High |
| FR2.3.1.2 | The system shall allow the user to initiate the joke feature using a voice command. | High |
| FR2.3.1.3 | The system shall retrieve a joke based on the user’s stored preferences. If no preferences are available, it shall select a joke at random from the default joke set. | High |
| FR2.3.1.4 | The system shall narrate the selected joke using the text-to-speech engine. | High |
| FR2.3.1.5 | The system shall display appropriate facial expressions on the screen while the joke is being narrated. | Medium |
| FR2.3.1.6 | The system shall trigger a predefined actuator-based gesture to accompany the joke delivery. If actuator gestures fail to trigger, the system shall still deliver the joke with screen-based visuals only. | Medium |
| FR2.3.1.7 | After the joke is delivered, the system shall optionally prompt the user to continue the interaction | Medium |
| FR2.3.1.8 | If the user responds with a new intent, the system shall detect the intent and route to the corresponding feature. | High |
| FR2.3.1.9 | If the joke database is not accessible, the system shall notify the user and log the issue. | High |
| FR2.3.1.10 | If the text-to-speech engine fails to initialize or narrate, the system shall inform the user and log a fallback event. | High |


**Module 3.2 \- Choose-Your-Own-Adventure Interactive Story**

| ID | Description | Priority |
| ----- | ----- | ----- |
| FR2.3.2.1 | When the Entertainment activity is initiated, the system shall provide visual and audio confirmation of readiness via the droid’s screen and speaker. | High |
| FR2.3.2.2 | The system shall allow the user to start an interactive story session using a voice command. | High |
| FR2.3.2.3 | The system shall narrate the interactive story using the text-to-speech (TTS) module. | High |
| FR2.3.2.4 | At predefined intervals or plot milestones, the system shall both display and narrate the decision options on-screen to the user during each decision point. | High |
| FR2.3.2.5 | The system shall dynamically generate the next part of the story in real-time based on the interpreted user decision. | High |
| FR2.3.2.6 | The system shall filter or adapt generated story content and choices to ensure age-appropriate, culturally sensitive, and emotionally safe storytelling. | Medium |
| FR2.3.2.7 | The system shall continue the loop of narration, prompting, listening, and generation until the story reaches a natural conclusion. | High |
| FR2.3.2.8 | The system shall log the entire session, including generated content, user decisions, and timestamps, to the user’s profile in the web dashboard. | Medium |
| FR2.3.2.9 | If the user does not respond at a decision point, the system shall re-prompt the user once. If still silent, the system shall select a default decision path based on prior context. | High |
| FR2.3.2.10 | If the user provides an unexpected answer, the system shall attempt to match the intent to one of the listed options, or regenerate options to better fit the user's input. | High |
| FR2.3.2.11 | If the NLP engine crashes or becomes unresponsive, the system shall display a fallback message, end the session gracefully, and log the error. | High |
| FR2.3.2.12 | If no microphone input is detected when expected, the system shall notify the user, display an error message, and log the issue. | High |


**Module 3.3 \- Watch a Dance Along to Music**

| ID | Description | Priority |
| ----- | ----- | ----- |
| FR2.3.3.1 | When the Entertainment activity is initiated, the system shall provide visual and audio confirmation of readiness via the droid’s screen and speaker. | High |
| FR2.3.3.2 | The system shall allow the user to initiate the dance feature via voice command. | High |
| FR2.3.3.3 | The system shall retrieve and display a list of available dance choreography options from the backend database. | High |
| FR2.3.3.4 | The system shall enable the user to select a dance routine via voice command. | High |
|  | The system shall play the selected music through the built-in speaker. |  |
| FR2.3.3.5 | The system shall perform actuator-based dance movements synchronized with the music tempo. | High |
| FR2.3.3.6 | The system shall display facial expressions on the screen during the dance to enhance emotional engagement. | Medium |
| FR2.3.3.7 | After completing the dance routine, the system shall prompt the user to ask if they would like an encore. | High |
| FR2.3.3.8 | The system shall recognize and process the user’s “yes” or “no” response for the encore prompt. | High |
| FR2.3.3.9 | If the user requests an encore, the system shall repeat the selected dance routine. | Medium |
| FR2.3.3.10 | If the user declines the encore, the system shall gracefully end the session and optionally offer a follow-up prompt. | High |
| FR2.3.3.11 | The system shall handle timeouts gracefully if the user does not respond during the selection or encore prompts | High |
| FR2.3.3.12 | The system shall continue music playback and facial expression display if actuator movement fails during the dance. | Medium |
| FR2.3.3.13 | The system shall notify the user in case of backend database unavailability or communication errors. | Medium |