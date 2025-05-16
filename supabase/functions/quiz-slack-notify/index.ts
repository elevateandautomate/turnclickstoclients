import { serve } from 'https://deno.land/std@0.177.0/http/server.ts'
import { corsHeaders } from '../_shared/cors.ts' // Import CORS headers

// SLACK_WEBHOOK_URL will be read from environment variables (.env file locally, or Supabase dashboard for deployed)
const SLACK_WEBHOOK_URL = Deno.env.get('SLACK_WEBHOOK_URL')

console.log(`Function 'quiz-slack-notify' up and running! Listening for requests.`)

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    console.log('OPTIONS request received, responding with CORS headers.');
    return new Response('ok', { headers: corsHeaders })
  }

  // Check if the request method is POST for actual data submission
  if (req.method !== 'POST') {
    console.log(`Method ${req.method} received, only POST allowed.`);
    return new Response(JSON.stringify({ error: 'Method Not Allowed. Please use POST.' }), {
      status: 405,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    })
  }

  try {
    console.log('POST request received. Processing...');
    const submissionData = await req.json()
    console.log('Received submissionData for Slack notification:', submissionData)

    if (!SLACK_WEBHOOK_URL) {
      console.error('SLACK_WEBHOOK_URL environment variable is not configured.')
      return new Response(JSON.stringify({ error: 'Slack webhook URL not configured on the server.' }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      })
    }

    // Construct the message payload for Slack
    const {
      niche = 'N/A',
      submitted_at,
      first_name = 'N/A',
      last_name = 'N/A',
      business_name = 'N/A',
      email = 'N/A',
      phone = 'N/A',
      total_score = 'N/A',
      growth_stifler_response = 'N/A',
      quiz_answers = {},
      primary_outcome_hint = 'N/A',
      source = 'N/A'
    } = submissionData

    const formattedSubmittedAt = submitted_at ? new Date(submitted_at).toLocaleString() : 'N/A';

    let answersText = 'No specific answers provided.';
    if (quiz_answers && typeof quiz_answers === 'object' && Object.keys(quiz_answers).length > 0) {
        answersText = Object.entries(quiz_answers)
            .map(([key, value]) => `*${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:* ${value}`)
            .join('\n');
    }

    const messageBody = {
      text: `New Quiz Submission: ${niche}`,
      blocks: [
        { type: 'header', text: { type: 'plain_text', text: `🚀 New Quiz Submission: ${niche}`, emoji: true } },
        { type: 'divider' },
        { type: 'section', fields: [
            { type: 'mrkdwn', text: `*Submitted At:*\n${formattedSubmittedAt}` },
            { type: 'mrkdwn', text: `*Source:*\n${source || 'Website Quiz'}` }
        ]},
        { type: 'section', fields: [
            { type: 'mrkdwn', text: `*First Name:*\n${first_name}` },
            { type: 'mrkdwn', text: `*Last Name:*\n${last_name}` }
        ]},
        { type: 'section', fields: [
            { type: 'mrkdwn', text: `*Business Name:*\n${business_name}` },
            { type: 'mrkdwn', text: `*Email:*\n<mailto:${email}|${email}>` }
        ]},
        { type: 'section', fields: [
            { type: 'mrkdwn', text: `*Phone:*\n${phone}` },
            { type: 'mrkdwn', text: `*Total Score:*\n${total_score}` }
        ]},
        { type: 'divider' },
        { type: 'section', text: { type: 'mrkdwn', text: `*💡 Hidden Growth-Stifler Response:*\n${growth_stifler_response}` }},
        { type: 'section', text: { type: 'mrkdwn', text: `*🧠 Primary Outcome Hint:*\n${primary_outcome_hint}` }},
        { type: 'divider' },
        { type: 'section', text: { type: 'mrkdwn', text: `*📝 Full Quiz Answers:*\n${answersText}` }},
      ],
    }

    console.log('Attempting to send data to Slack...');
    const slackResponse = await fetch(SLACK_WEBHOOK_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }, // Slack expects JSON
      body: JSON.stringify(messageBody),
    })

    if (!slackResponse.ok) {
      const errorBody = await slackResponse.text()
      console.error(`Error sending to Slack: ${slackResponse.status} ${slackResponse.statusText}`, errorBody)
      return new Response(JSON.stringify({ error: `Failed to send notification to Slack. Status: ${slackResponse.status}` }), {
        status: 502, // Bad Gateway
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      })
    }

    console.log('Successfully sent data to Slack.')
    return new Response(JSON.stringify({ message: 'Quiz data processed for Slack notification successfully!' }), {
      status: 200,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    })

  } catch (error) {
    console.error('Error in quiz-slack-notify Edge Function:', error.message, error.stack)
    return new Response(JSON.stringify({ error: error.message || 'Internal Server Error in Edge Function' }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    })
  }
})