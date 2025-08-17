import React, { useState } from 'react';

const Home: React.FC = () => {
    const [locationType, setLocationType] = useState<'address' | 'coordinates'>('address');
    const [address, setAddress] = useState('');
    const [latitude, setLatitude] = useState('');
    const [longitude, setLongitude] = useState('');
    const [station, setStation] = useState<string | null>(null);
    const [stationAddress, setStationAddress] = useState<string | null>(null);
    const [city, setCity] = useState<string | null>(null);
    const [state, setState] = useState<string | null>(null);
    const [zip, setZip] = useState<string | null>(null);
    const [directions, setDirections] = useState<Array<any>>([]);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setStation(null);
        setStationAddress(null);
        setCity(null);
        setState(null);
        setZip(null);
        setDirections([]);

        const apiUrl = `${process.env.REACT_APP_API_URL}/api`;

        let body: any = { location_type: locationType };
        if (locationType === 'address') {
            body.address = address;
        } else {
            body.latitude = latitude ? parseFloat(latitude) : undefined;
            body.longitude = longitude ? parseFloat(longitude) : undefined;
        }

        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            });
            const data = await response.json();
            if (!response.ok) {
                setError(data.detail || 'Unknown error');
            } else {
                setStation(data.station.properties.name);
                setStationAddress(data.station.properties.address);
                setCity(data.station.properties.city);
                setState(data.station.properties.state);
                setZip(data.station.properties.zip);
                setDirections(data.directions || []);
            }
        } catch (err) {
            setError('Network error');
        }
    };

    return (
        <div>
            <h1>SEPTA Walking Application Demo</h1>
            <p>
                Enter an address or coordinates below to find the nearest
                SEPTA station and walking directions to it.
            </p>
            <form onSubmit={handleSubmit}>
                <div>
                    <label>
                        Location Type:
                        <select
                            value={locationType}
                            onChange={e => setLocationType(e.target.value as 'address' | 'coordinates')}
                        >
                            <option value="address">Address</option>
                            <option value="coordinates">Coordinates</option>
                        </select>
                    </label>
                </div>
                {locationType === 'address' ? (
                    <div>
                        <label>
                            Address:
                            <input
                                type="text"
                                value={address}
                                onChange={e => setAddress(e.target.value)}
                                required
                            />
                        </label>
                    </div>
                ) : (
                    <><div>
                        <label>
                            Latitude:
                            <input
                                type="number"
                                step="any"
                                value={latitude}
                                onChange={e => setLatitude(e.target.value)}
                                required />
                        </label>
                    </div>
                    <div>
                        <label>
                            Longitude:
                            <input
                                type="number"
                                step="any"
                                value={longitude}
                                onChange={e => setLongitude(e.target.value)}
                                required />
                        </label>
                    </div></>
                )}
                <button type="submit">Find Nearest Station</button>
            </form>
            {error && <div style={{ color: 'red' }}>Error: {error}</div>}
            {station && (
                <div>
                    <h2>Result</h2>
                    <h3>Station</h3>
                    <p>{station}</p>
                    <h3>Address</h3>
                    <p>{stationAddress}<br/>
                    {city}, {state}, {zip}</p>
                </div>
            )}
            {directions.length > 0 && (
                <div>
                    <h3>Walking Directions</h3>
                    <ol>
                        {directions.map((step, idx) => (
                            <li key={idx} dangerouslySetInnerHTML={{ __html: `${step.instruction} (${step.distance})` }}></li>
                        ))}
                    </ol>
                </div>
            )}
        </div>
    );
};

export default Home;
