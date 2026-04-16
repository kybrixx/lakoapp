// OSM Map System for Lako
class MapManager {
    constructor() {
        this.map = null;
        this.markers = [];
        this.currentLocation = null;
        this.heatmapLayer = null;
        this.routingControl = null;
        this.vendors = [];
        this.defaultCenter = [14.5995, 120.9842];
        this.defaultZoom = 13;
    }

    init(elementId, options = {}) {
        const element = document.getElementById(elementId);
        if (!element) return null;
        
        const center = options.center || this.defaultCenter;
        const zoom = options.zoom || this.defaultZoom;
        
        this.map = L.map(element).setView(center, zoom);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(this.map);
        
        // Add scale control
        L.control.scale({ imperial: false, metric: true }).addTo(this.map);
        
        return this.map;
    }

    setView(lat, lng, zoom = 14) {
        if (this.map) {
            this.map.setView([lat, lng], zoom);
        }
    }

    addMarker(lat, lng, options = {}) {
        if (!this.map) return null;
        
        const marker = L.marker([lat, lng], options).addTo(this.map);
        
        if (options.popup) {
            marker.bindPopup(options.popup);
        }
        
        if (options.tooltip) {
            marker.bindTooltip(options.tooltip);
        }
        
        if (options.onClick) {
            marker.on('click', options.onClick);
        }
        
        this.markers.push(marker);
        return marker;
    }

    addVendorMarker(vendor) {
        if (!vendor.latitude || !vendor.longitude) return null;
        
        const popupContent = `
            <div style="min-width: 200px;">
                <strong>${vendor.business_name || vendor.name}</strong><br>
                <small>${vendor.category}</small><br>
                <span style="color: #fbbf24;">${'★'.repeat(Math.floor(vendor.rating || 0))}${'☆'.repeat(5 - Math.floor(vendor.rating || 0))}</span>
                <span>${vendor.rating || 0} (${vendor.review_count || 0})</span><br>
                <button onclick="window.viewVendor('${vendor.id}')" style="margin-top: 8px; padding: 6px 12px; background: #0f5c2f; color: white; border: none; border-radius: 20px; cursor: pointer; width: 100%;">View Details</button>
            </div>
        `;
        
        return this.addMarker(vendor.latitude, vendor.longitude, {
            popup: popupContent,
            tooltip: vendor.business_name || vendor.name
        });
    }

    addVendorMarkers(vendors) {
        this.clearMarkers();
        this.vendors = vendors;
        vendors.forEach(v => this.addVendorMarker(v));
    }

    addCurrentLocationMarker(lat, lng) {
        const icon = L.divIcon({
            html: '<div style="width: 16px; height: 16px; background: #3b82f6; border: 3px solid white; border-radius: 50%; box-shadow: 0 2px 8px rgba(0,0,0,0.2);"></div>',
            className: 'current-location-marker',
            iconSize: [16, 16]
        });
        
        return this.addMarker(lat, lng, {
            icon,
            popup: 'You are here'
        });
    }

    clearMarkers() {
        this.markers.forEach(m => this.map.removeLayer(m));
        this.markers = [];
    }

    async getCurrentLocation() {
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject(new Error('Geolocation not supported'));
                return;
            }
            
            navigator.geolocation.getCurrentPosition(
                (pos) => {
                    this.currentLocation = {
                        lat: pos.coords.latitude,
                        lng: pos.coords.longitude
                    };
                    resolve(this.currentLocation);
                },
                (err) => reject(err),
                { enableHighAccuracy: true, timeout: 10000 }
            );
        });
    }

    async centerOnUser() {
        try {
            const pos = await this.getCurrentLocation();
            this.setView(pos.lat, pos.lng);
            this.addCurrentLocationMarker(pos.lat, pos.lng);
            return pos;
        } catch (error) {
            console.error('Error getting location:', error);
            showToast('Could not get your location', 'error');
            return null;
        }
    }

    fitToMarkers() {
        if (this.markers.length && this.map) {
            const group = L.featureGroup(this.markers);
            this.map.fitBounds(group.getBounds(), { padding: [50, 50] });
        }
    }

    async loadNearbyVendors(lat, lng, radius = 10) {
        try {
            const data = await api.getNearbyVendors(lat, lng, radius);
            this.addVendorMarkers(data.vendors || []);
            return data.vendors;
        } catch (error) {
            console.error('Error loading vendors:', error);
            return [];
        }
    }

    async getRoute(startLat, startLng, endLat, endLng, mode = 'driving') {
        if (!this.map) return null;
        
        // Remove existing route
        if (this.routingControl) {
            this.map.removeControl(this.routingControl);
        }
        
        // Use OSRM for routing
        const url = `https://router.project-osrm.org/route/v1/${mode}/${startLng},${startLat};${endLng},${endLat}?overview=full&geometries=geojson`;
        
        try {
            const response = await fetch(url);
            const data = await response.json();
            
            if (data.routes && data.routes[0]) {
                const route = data.routes[0];
                const coordinates = route.geometry.coordinates.map(c => [c[1], c[0]]);
                
                const routeLine = L.polyline(coordinates, {
                    color: '#0f5c2f',
                    weight: 4,
                    opacity: 0.8
                }).addTo(this.map);
                
                this.markers.push(routeLine);
                
                return {
                    distance: route.distance / 1000,
                    duration: route.duration / 60
                };
            }
        } catch (error) {
            console.error('Error getting route:', error);
        }
        
        return null;
    }

    async toggleHeatmap() {
        if (this.heatmapLayer) {
            this.map.removeLayer(this.heatmapLayer);
            this.heatmapLayer = null;
        } else {
            try {
                const data = await api.getHeatmap();
                const points = data.points.map(p => [p.latitude, p.longitude, p.weight]);
                
                this.heatmapLayer = L.heatLayer(points, {
                    radius: 25,
                    blur: 15,
                    maxZoom: 17,
                    gradient: {
                        0.2: '#10b981',
                        0.4: '#84cc16',
                        0.6: '#eab308',
                        0.8: '#f97316',
                        1.0: '#dc2626'
                    }
                }).addTo(this.map);
            } catch (error) {
                console.error('Error loading heatmap:', error);
            }
        }
    }

    addSearchControl() {
        if (!this.map) return;
        
        const searchControl = L.control({ position: 'topleft' });
        
        searchControl.onAdd = () => {
            const div = L.DomUtil.create('div', 'map-search-control');
            div.innerHTML = `
                <div style="background: white; padding: 8px; border-radius: 40px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <input type="text" placeholder="Search location..." id="mapSearchInput" 
                           style="border: none; outline: none; padding: 8px 16px; width: 200px; border-radius: 40px;">
                    <button onclick="window.searchLocation()" style="background: #0f5c2f; color: white; border: none; padding: 8px 16px; border-radius: 40px; cursor: pointer;">Go</button>
                </div>
            `;
            return div;
        };
        
        searchControl.addTo(this.map);
    }

    addLayerControl(baseLayers, overlayLayers) {
        if (!this.map) return;
        L.control.layers(baseLayers, overlayLayers).addTo(this.map);
    }

    on(event, callback) {
        if (this.map) {
            this.map.on(event, callback);
        }
    }

    invalidateSize() {
        if (this.map) {
            this.map.invalidateSize();
        }
    }
}

const mapManager = new MapManager();

// Global map functions
window.viewVendor = (id) => {
    window.location.href = `/pages/customer/vendor-profile.html?id=${id}`;
};

window.searchLocation = async () => {
    const input = document.getElementById('mapSearchInput');
    if (!input || !input.value) return;
    
    try {
        const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(input.value)}`);
        const data = await response.json();
        
        if (data.length) {
            const lat = parseFloat(data[0].lat);
            const lng = parseFloat(data[0].lon);
            mapManager.setView(lat, lng, 15);
            mapManager.addMarker(lat, lng, { popup: data[0].display_name });
        }
    } catch (error) {
        console.error('Search error:', error);
    }
};