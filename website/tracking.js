// User Journey Tracking Script
document.addEventListener('DOMContentLoaded', function() {
  // Create flow tracking ID if it doesn't exist
  if (!localStorage.getItem('flow_hash')) {
    const flowHash = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
    localStorage.setItem('flow_hash', flowHash);
  }
  
  // Get URL parameters
  const params = new URLSearchParams(window.location.search);
  
  // Store UTM parameters (only if not already stored or if new values provided)
  if (!localStorage.getItem('traffic_source') || params.get('utm_source') || params.get('source')) {
    localStorage.setItem('traffic_source', params.get('utm_source') || params.get('source') || document.referrer || 'direct');
  }
  
  if (!localStorage.getItem('utm_medium') || params.get('utm_medium')) {
    localStorage.setItem('utm_medium', params.get('utm_medium') || '');
  }
  
  if (!localStorage.getItem('utm_campaign') || params.get('utm_campaign')) {
    localStorage.setItem('utm_campaign', params.get('utm_campaign') || '');
  }
  
  if (!localStorage.getItem('landing_page')) {
    localStorage.setItem('landing_page', window.location.href);
    localStorage.setItem('entry_point', 'landing_page');
  }
  
  // Determine page type
  const path = window.location.pathname;
  let pageType = 'other';
  
  if (path.includes('index.html') || path === '/' || path.endsWith('/')) {
    pageType = 'home';
  } else if (path.includes('-quiz.html')) {
    pageType = 'quiz';
  } else if (path.includes('-variant-')) {
    pageType = 'quiz_result';
  } else if (path.includes('universal-application-form.html')) {
    pageType = 'application';
  } else if (path.includes('niches/')) {
    pageType = 'niche';
  }
  
  // Extract niche, bucket, and variant from URL if available
  let niche = '';
  let bucket = '';
  let variant = '';
  
  if (params.get('niche')) {
    niche = params.get('niche');
  } else if (path.includes('/quiz-applications/')) {
    const pathParts = path.split('/');
    const nicheIndex = pathParts.findIndex(part => part === 'quiz-applications');
    if (nicheIndex >= 0 && pathParts.length > nicheIndex + 1) {
      niche = pathParts[nicheIndex + 1];
    }
  } else if (path.includes('niches/')) {
    const match = path.match(/niches\/([^-/]+)/);
    if (match && match[1]) {
      niche = match[1];
    }
  }
  
  if (params.get('bucket')) {
    bucket = params.get('bucket');
  } else if (path.includes('variant-')) {
    const pathParts = path.split('/');
    const bucketPartIndex = pathParts.findIndex(part => part.includes('variant-'));
    if (bucketPartIndex > 0) {
      bucket = pathParts[bucketPartIndex - 1];
    }
  }
  
  if (params.get('variant')) {
    variant = params.get('variant');
  } else if (path.includes('variant-')) {
    const match = path.match(/variant-([a-c]-[^.]+)/i);
    if (match && match[1]) {
      variant = match[1];
    }
  }
  
  // Track page visit in Supabase if available
  if (typeof supabase !== 'undefined') {
    try {
      const supabaseClient = supabase.createClient(
        'https://eumhqssfvkyuepyrtlqj.supabase.co',
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1bWhxc3Nmdmt5dWVweXJ0bHFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY1NjE0MDEsImV4cCI6MjA2MjEzNzQwMX0.w-UzQq1G6GIinBdlIcW34KBSoeaAK-knNs4AvL8ct64'
      );
      
      supabaseClient.from('tctc_user_flow').insert([{
        user_first_name: params.get('firstName') || localStorage.getItem('user_first_name') || '',
        user_last_name: params.get('lastName') || localStorage.getItem('user_last_name') || '',
        user_business_name: params.get('businessName') || localStorage.getItem('user_business_name') || '',
        user_email: params.get('email') || localStorage.getItem('user_email') || '',
        action_type: 'page_view',
        niche: niche,
        page_bucket: bucket,
        page_variant: variant,
        original_source: localStorage.getItem('traffic_source') || 'direct',
        track_source: params.get('track_source') || localStorage.getItem('track_source') || 'direct',
        quiz_score: params.get('score') || 0,
        source_page: document.referrer,
        traffic_source: localStorage.getItem('traffic_source') || 'direct',
        utm_medium: localStorage.getItem('utm_medium') || '',
        utm_campaign: localStorage.getItem('utm_campaign') || '',
        flow_hash: localStorage.getItem('flow_hash') || ''
      }]).then(result => {
        console.log('Page view tracked:', result);
      }).catch(error => {
        console.error('Error tracking page view:', error);
      });
      
      // Store user data from URL parameters if available
      if (params.get('firstName')) {
        localStorage.setItem('user_first_name', params.get('firstName'));
      }
      if (params.get('lastName')) {
        localStorage.setItem('user_last_name', params.get('lastName'));
      }
      if (params.get('businessName')) {
        localStorage.setItem('user_business_name', params.get('businessName'));
      }
      if (params.get('email')) {
        localStorage.setItem('user_email', params.get('email'));
      }
      if (params.get('track_source')) {
        localStorage.setItem('track_source', params.get('track_source'));
      }
      
    } catch (e) {
      console.error('Error tracking page view in Supabase:', e);
    }
  }
  
  // Add tracking parameters to all links to keep the flow
  setTimeout(function() {
    const allLinks = document.querySelectorAll('a');
    allLinks.forEach(link => {
      try {
        if (link.href && link.href.includes(window.location.hostname) && !link.href.includes('#')) {
          const url = new URL(link.href);
          
          // Don't modify links that already have tracking parameters
          if (!url.searchParams.has('flow_hash')) {
            // Add tracking parameters
            url.searchParams.append('flow_hash', localStorage.getItem('flow_hash') || '');
            
            if (localStorage.getItem('traffic_source')) {
              url.searchParams.append('source', localStorage.getItem('traffic_source'));
            }
            
            if (localStorage.getItem('utm_medium')) {
              url.searchParams.append('utm_medium', localStorage.getItem('utm_medium'));
            }
            
            if (localStorage.getItem('utm_campaign')) {
              url.searchParams.append('utm_campaign', localStorage.getItem('utm_campaign'));
            }
            
            if (niche) {
              url.searchParams.append('niche', niche);
            }
            
            link.href = url.toString();
          }
        }
      } catch (e) {
        console.error('Error adding tracking to link:', e);
      }
    });
  }, 500);
});

// Add tracking source to all forms
document.addEventListener('DOMContentLoaded', function() {
  const forms = document.querySelectorAll('form');
  forms.forEach(form => {
    form.addEventListener('submit', function(e) {
      // Don't add hidden fields if they already exist
      if (!this.querySelector('input[name="flow_hash"]')) {
        // Add tracking data as hidden fields
        const fields = [
          { name: 'flow_hash', value: localStorage.getItem('flow_hash') || '' },
          { name: 'traffic_source', value: localStorage.getItem('traffic_source') || 'direct' },
          { name: 'utm_medium', value: localStorage.getItem('utm_medium') || '' },
          { name: 'utm_campaign', value: localStorage.getItem('utm_campaign') || '' },
          { name: 'landing_page', value: localStorage.getItem('landing_page') || '' },
          { name: 'entry_point', value: localStorage.getItem('entry_point') || '' }
        ];
        
        fields.forEach(field => {
          const input = document.createElement('input');
          input.type = 'hidden';
          input.name = field.name;
          input.value = field.value;
          this.appendChild(input);
        });
      }
    });
  });
}); 