const API_ENDPOINT = 'https://fboir4xj6j.execute-api.us-east-1.amazonaws.com/prod/synthesize';

class VoiceSynthApp {
    constructor() {
        this.textInput = document.getElementById('textInput');
        this.wordCount = document.getElementById('wordCount');
        this.languageSelect = document.getElementById('languageSelect');
        this.voiceSelect = document.getElementById('voiceSelect');
        this.speedSelect = document.getElementById('speedSelect');
        this.convertBtn = document.getElementById('convertBtn');
        this.loading = document.getElementById('loading');
        this.result = document.getElementById('result');
        this.error = document.getElementById('error');
        this.audioPlayer = document.getElementById('audioPlayer');
        this.downloadBtn = document.getElementById('downloadBtn');
        this.shareBtn = document.getElementById('shareBtn');
        this.translationInfo = document.getElementById('translationInfo');
        this.translatedText = document.getElementById('translatedText');
        
        this.currentAudioUrl = null;
        this.voices = {
            'en-US': [
                { value: 'Joanna', name: 'Joanna (Female)' },
                { value: 'Matthew', name: 'Matthew (Male)' },
                { value: 'Ivy', name: 'Ivy (Child)' },
                { value: 'Justin', name: 'Justin (Male)' }
            ],
            'en-GB': [
                { value: 'Amy', name: 'Amy (Female)' },
                { value: 'Brian', name: 'Brian (Male)' },
                { value: 'Emma', name: 'Emma (Female)' }
            ],
            'es-ES': [
                { value: 'Lucia', name: 'Lucia (Female)' },
                { value: 'Enrique', name: 'Enrique (Male)' }
            ],
            'fr-FR': [
                { value: 'Celine', name: 'Celine (Female)' },
                { value: 'Mathieu', name: 'Mathieu (Male)' }
            ],
            'de-DE': [
                { value: 'Marlene', name: 'Marlene (Female)' },
                { value: 'Hans', name: 'Hans (Male)' }
            ],
            'it-IT': [
                { value: 'Carla', name: 'Carla (Female)' },
                { value: 'Giorgio', name: 'Giorgio (Male)' }
            ],
            'pt-BR': [
                { value: 'Vitoria', name: 'Vitoria (Female)' },
                { value: 'Ricardo', name: 'Ricardo (Male)' }
            ],
            'ja-JP': [
                { value: 'Mizuki', name: 'Mizuki (Female)' },
                { value: 'Takumi', name: 'Takumi (Male)' }
            ]
        };
        
        this.init();
    }
    
    init() {
        this.convertBtn.addEventListener('click', () => this.convertText());
        this.textInput.addEventListener('input', () => this.updateWordCount());
        this.languageSelect.addEventListener('change', () => this.updateVoices());
        this.speedSelect.addEventListener('change', () => this.updateSpeed());
        this.downloadBtn.addEventListener('click', () => this.downloadAudio());
        this.shareBtn.addEventListener('click', () => this.shareApp());
        this.updateWordCount();
        this.updateVoices();
    }
    
    updateWordCount() {
        const text = this.textInput.value;
        // Sanitize and validate input
        const sanitizedText = text.replace(/<[^>]*>/g, ''); // Remove HTML tags
        this.wordCount.textContent = sanitizedText.length;
        this.convertBtn.disabled = sanitizedText.trim().length === 0;
        
        // Update textarea with sanitized content if needed
        if (text !== sanitizedText) {
            this.textInput.value = sanitizedText;
        }
    }
    
    updateVoices() {
        const selectedLanguage = this.languageSelect.value;
        const availableVoices = this.voices[selectedLanguage] || [];
        
        // Clear current options
        this.voiceSelect.innerHTML = '';
        
        // Add new options
        availableVoices.forEach(voice => {
            const option = document.createElement('option');
            option.value = voice.value;
            option.textContent = voice.name;
            this.voiceSelect.appendChild(option);
        });
    }
    
    updateSpeed() {
        const speed = this.speedSelect.value;
        if (this.audioPlayer.src) {
            this.audioPlayer.playbackRate = parseFloat(speed);
        }
    }
    
    downloadAudio() {
        if (this.currentAudioUrl) {
            const link = document.createElement('a');
            link.href = this.currentAudioUrl;
            link.download = `speech-${Date.now()}.mp3`;
            link.click();
        }
    }
    
    shareApp() {
        if (navigator.share) {
            navigator.share({
                title: 'Voice Synthesis App',
                text: 'Convert text to speech with this amazing app!',
                url: window.location.href
            });
        } else {
            navigator.clipboard.writeText(window.location.href).then(() => {
                alert('App URL copied to clipboard!');
            });
        }
    }
    
    async convertText() {
        const text = this.textInput.value.trim();
        const voice = this.voiceSelect.value;
        
        if (!text) return;
        
        this.showLoading();
        
        try {
            const response = await fetch(API_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text.replace(/<[^>]*>/g, ''), // Sanitize HTML
                    voice: voice.replace(/<[^>]*>/g, ''),
                    language: this.languageSelect.value.replace(/<[^>]*>/g, '')
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.audioUrl) {
                this.showResult(data.audioUrl, data.originalText, data.translatedText);
            } else if (data.error) {
                throw new Error(data.error);
            } else {
                throw new Error('No audio URL received');
            }
            
        } catch (error) {
            console.error('Error:', error);
            console.error('Response status:', error.message);
            this.showError(`Failed to convert text to speech: ${error.message}`);
        }
    }
    
    showLoading() {
        this.loading.classList.remove('hidden');
        this.result.classList.add('hidden');
        this.error.classList.add('hidden');
        this.convertBtn.disabled = true;
    }
    
    showResult(audioUrl, originalText, translatedText) {
        this.loading.classList.add('hidden');
        this.result.classList.remove('hidden');
        this.error.classList.add('hidden');
        this.convertBtn.disabled = false;
        
        this.currentAudioUrl = audioUrl;
        this.audioPlayer.src = audioUrl;
        this.audioPlayer.playbackRate = parseFloat(this.speedSelect.value);
        
        // Show translation info if text was translated
        console.log('Original:', originalText);
        console.log('Translated:', translatedText);
        if (originalText && translatedText && originalText !== translatedText) {
            this.translatedText.textContent = translatedText;
            this.translationInfo.classList.remove('hidden');
            console.log('Showing translation info');
        } else {
            this.translationInfo.classList.add('hidden');
            console.log('Hiding translation info');
        }
        
        // Show download and share buttons
        this.downloadBtn.classList.remove('hidden');
        this.shareBtn.classList.remove('hidden');
        
        // Auto-play the audio
        this.audioPlayer.play().catch(e => {
            console.log('Auto-play prevented by browser:', e);
        });
    }
    
    showError(message) {
        this.loading.classList.add('hidden');
        this.result.classList.add('hidden');
        this.error.classList.remove('hidden');
        // Sanitize error message to prevent XSS
        this.error.textContent = String(message).replace(/<[^>]*>/g, '');
        this.convertBtn.disabled = false;
        
        // Hide download and share buttons on error
        this.downloadBtn.classList.add('hidden');
        this.shareBtn.classList.add('hidden');
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new VoiceSynthApp();
});
