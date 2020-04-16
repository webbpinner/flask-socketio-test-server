import React from 'react';
import logo from './logo.svg';
import io from 'socket.io-client';
import axios from 'axios';
import './App.css';

const API_ROOT_URL = 'http://localhost:5000';
const WS_ROOT_URL = 'ws://localhost:5000';

class App extends React.Component {

  constructor(props) {
    super(props)

    this.state = {
      deployments: [{status: 'fetching'}],
      deployment_name: ''
    }

    this.deployments_client = null;

    this.fetchDeployments = this.fetchDeployments.bind(this);
    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  componentDidMount() {

    this.fetchDeployments();

    try {
      this.deployments_client = io(WS_ROOT_URL + '/deployments');

      this.deployments_client.on('deployment_updated', (update) => {this.deploymentUpdated(update)});

    } catch(error) {
      console.log(error);
      this.setState({deployments:[{status: 'Unable to connect to server'}]});
      throw(error);
    }
  }

  componentDidUpdate(prevProps, prevState) {
  }

  componentWillUnmount() {
    this.deployments_client.disconnect();
  }

  deploymentUpdated(update) {
    console.log("message recieved via websocket connection:", update)
    this.fetchDeployments();
  }

  async fetchDeployments() {
    console.log("fetching deployments from API")
    const deployments = await axios.get(`${API_ROOT_URL}/api/v1/deployments`
    ).then(response => {
      console.log("response from API:", response.data.deployments);
      return response.data.deployments;
    }).catch(error => {
      console.log(error);
      return [{status: 'Unable to connect to server'}];
    })

    this.setState({deployments});
  }


  handleChange(event) {
    this.setState({deployment_name: event.target.value});
  }

  handleSubmit(e) {
    e.preventDefault();

    axios.put(`${API_ROOT_URL}/api/v1/deployment/1`, {name: this.state.deployment_name}
    ).then(response => {
      this.setState({deployment_name:''})
    }).catch(error => {
      console.log(error);
      this.setState({deployment_name:'', deployments:[{status: error}]});
    })
  }

  render() {

    return (
      <div className="App">
        <header className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
          <form onSubmit={this.handleSubmit}>
            <label>Set a new deployment name: </label>
            <input type="text" value={this.state.deployment_name} onChange={this.handleChange} id="name" name="name"/>
            <button>Submit</button>
          </form> 
          {
            this.state.deployments.map((deployment, idx) => {
              return <span key={idx}>
                {(deployment.status) ? `Status: ${deployment.status}` : ''}<br/>
                {(deployment.name) ? `Name from API: ${deployment.name}` : ''}<br/>
              </span>
            })
          }
        </header>
      </div>
    );
  }
}

export default App;
