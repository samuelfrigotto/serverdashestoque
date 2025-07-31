// Save this as BeforeUnloadComponent.js
import React, { useEffect } from 'react';
import { useDashCallback } from 'dash';

const BeforeUnloadComponent = () => {
    const sendUpdate = useDashCallback();

    useEffect(() => {
        const handleBeforeUnload = (event) => {
            sendUpdate();
            event.preventDefault();
            event.returnValue = '';
        };

        window.addEventListener('beforeunload', handleBeforeUnload);

        return () => {
            window.removeEventListener('beforeunload', handleBeforeUnload);
        };
    }, [sendUpdate]);

    return null;
};

export default BeforeUnloadComponent;