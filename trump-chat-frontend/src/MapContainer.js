// src/MapContainer.js
import React, { useEffect } from 'react';

function MapContainer() {
  useEffect(() => {
    // S'assurer que window.svgMap est bien chargé
    if (window.svgMap && window.svgMapDataGPD) {
      new window.svgMap({
        targetElementID: 'svgMapGPD',
        data: window.svgMapDataGPD,
        mouseWheelZoomEnabled: true,
        mouseWheelZoomWithKey: true
      });
    } else {
      console.error("svgMap ou svgMapDataGPD n'est pas défini!");
    }
  }, []);

  return (
    <div
      id="svgMapGPD"
      style={{ width: '100%', height: '100%' }}
    />
  );
}

export default MapContainer;
