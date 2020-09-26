import React from 'react';
import ReactDOM from 'react-dom';
import { StylesProvider } from '@material-ui/core/styles';

import App from './App';
import "./index.css";
import * as serviceWorker from './serviceWorker';

ReactDOM.render(
    <React.StrictMode>
        <StylesProvider injectFirst>
            <App />
        </StylesProvider>
    </React.StrictMode>,
    document.getElementById('root')
);

serviceWorker.unregister();
