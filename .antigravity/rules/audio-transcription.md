---
trigger: always_on
description: Always transcribe user voice/audio notes at the very beginning of the response
---

# Audio Note Transcription Rule

Whenever the user submits an audio recording or voice note in their prompt:

## Requirements

1. **Always Lead with the Audio Transcription**:
   - The very first section of the agent's response must display a faithful, word-for-word transcription of the spoken audio.
   - Format the transcription clearly at the top using a dedicated block or quote, for example:
     ```markdown
     > 🎙️ **Audio Transcription:**  
     > *"Exact words spoken by the user..."*
     ```

2. **Preserve the Original Spoken Language**:
   - The transcription must remain in the language spoken by the user (e.g. Polish or English) so that the user can immediately verify acoustic and semantic accuracy.

3. **Proceed with Action Immediately After**:
   - Following the transcription block, proceed directly with addressing the prompt, answering questions, or updating and linking notes according to the user's intent.
