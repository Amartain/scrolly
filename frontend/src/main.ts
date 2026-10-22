import { mount } from 'svelte';
import App from './App.svelte';
import './styles/fonts.css';
import './styles/tokens/base.css';
import './styles/tokens/serene-day.css';
import './styles/tokens/serene-dusk.css';
import './styles/tokens/pavilion-teal.css';
import './styles/tokens/pavilion-crimson.css';
import './styles/tokens/pavilion-purple.css';
import './styles/global.css';
import './styles/glitch.css';
import './styles/ceremony-thunder.css';
import './styles/ceremony-thunder-motion.css';
import './styles/ceremony-keyframes.css';

mount(App, { target: document.getElementById('app')! });
