/* React component for the plotly graph showcasing total monthly budget spent, receiving data from endpoints to populate data */

import React, { useEffect, useState } from 'react';
import Plot from 'react-plotly.js';
import axios from 'axios';

// TODO TODO TODO - REFACTOR USING CHAKARA COMPONENTS FOR MORE CONSISTENT STYLING (DONUT CHART)

interface BudgetSpentData {
    month: string;
    budgeted: number;
    spent: number;
}

const BudgetSpent: React.FC = () => {
    const [data, setData] = useState<BudgetSpentData[]>([]);

    // Fetch data from the backend API
    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await axios.get<BudgetSpentData[]>('/api/budget-spent');
                setData(response.data);
            } catch (error) {
                console.error('Error fetching budget spent data:', error);
            }
        };

        // call fetchData when component mounts
        fetchData();
    }, []);

    // Map response data to plotly format
    const months = data.map(d => d.month);
    const budgeted = data.map(d => d.budgeted);
    const spent = data.map(d => d.spent);

    // Return the Plotly graph (currently not formatted)
    return (
        <div>
            <h3>Monthly Budget Spent</h3>
            <Plot
                data={[
                    { x: months, y: budgeted, type: 'bar', name: 'Budgeted' },
                    { x: months, y: spent, type: 'bar', name: 'Spent' },
                ]}
                layout={{ barmode: 'group', title: 'Budget vs Spent', autosize: true }}
                style={{ width: '100%', height: '400px' }}
            />
        </div>
    );
}

export default BudgetSpent;
