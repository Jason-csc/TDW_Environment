import React from 'react';
import PropTypes from 'prop-types';
import TaskBox from './taskbox';
import ControlBox from './controlbox';
import ChatBox from './chatbox';
import InfoBox from './infobox';


class Post extends React.Component {
    constructor(props) {
        // Initialize mutable state
        super(props);
        this.state = {
            chats: [],
            num: 0,
            value: '',
            obj: [],
            positions: [],
            status: '', //PICK or DROP
            task: [],
            canPick: true,
            canDrop: true,
            canShare: true,
            playerTurn: true,
        };
        this.handleNewComment = this.handleNewComment.bind(this);
        this.handleChange = this.handleChange.bind(this);
        this.handleStatus = this.handleStatus.bind(this);
        this.handleNewInfo = this.handleNewInfo.bind(this);
        this.changeTurn = this.changeTurn.bind(this);
    }



    componentDidMount() {
        if (document.body.id == "player1" || document.body.id == "player2") {
            this.setChecker_chat = setInterval(this.checkdbchat.bind(this), 500);
        }
        else if (document.body.id == "player_bot") {
            this.setChecker_turn = setInterval(this.checkturn.bind(this), 400);
        }
        this.setChecker_obj = setInterval(this.checkdbobj.bind(this), 600);
        this.setChecker_task = setInterval(this.checktask.bind(this), 600);
        const { url } = this.props;
        fetch(`${url}?player=${document.body.id}`, { credentials: 'same-origin' })
            .then((response) => {
                if (!response.ok) throw Error(response.statusText);
                return response.json();
            })
            .then((data) => {
                this.setState({
                    chats: data.chats,
                    num: data.num,
                    value: '',
                    obj: [],
                    positions: data.positions,
                    status: data.status
                });
            })
            .catch((error) => console.log(error));
    }

    checkdbobj() {
        const { url2 } = this.props;
        fetch(`${url2}?player=${document.body.id}`, { credentials: 'same-origin' })
            .then((response) => {
                if (!response.ok) throw Error(response.statusText);
                return response.json();
            })
            .then((data) => {
                this.setState({
                    obj: data.obj
                });
            })
            .catch((error) => console.log(error));
    }

    checktask() {
        fetch(`/api/v1/tasks/?player=${document.body.id}`, { credentials: 'same-origin' })
            .then((response) => {
                if (!response.ok) throw Error(response.statusText);
                return response.json();
            })
            .then((data) => {
                this.setState({
                    task: data.tasks
                });
                console.log("tasks")
                console.log(data.tasks);
            })
            .catch((error) => console.log(error));
    }

    checkturn() {
        fetch(`/api/v1/turn`, { credentials: 'same-origin' })
            .then((response) => {
                if (!response.ok) throw Error(response.statusText);
                return response.json();
            })
            .then((data) => {
                this.setState({
                    canPick: data.canPick,
                    canDrop: data.canDrop,
                    canShare: data.canShare,
                    playerTurn: data.playerTurn,

                });
            })
            .catch((error) => console.log(error));
    }

    checkdbchat() {
        const { url } = this.props;
        fetch(url, { credentials: 'same-origin' })
            .then((response) => {
                if (!response.ok) throw Error(response.statusText);
                return response.json();
            })
            .then((data) => {
                if (data.num > this.state.num) {
                    this.setState({
                        chats: data.chats,
                        num: data.num,
                    });
                }
            })
            .catch((error) => console.log(error));
    }

    changeTurn() {
        fetch(`/api/v1/changeturn/`, {
            method: 'PUT',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
            }
        })
            .then((response) => {
                if (!response.ok) throw Error(response.statusText);
                return response.json();
            })
            .then({})
            .catch((error) => console.log(error));

    }

    handleNewComment(event) {
        const { value } = this.state;
        // console.log("enter herere");
        fetch(`/api/v1/addchats/`,
            {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: value, owner: document.body.id }),
            })
            .then((response) => {
                if (!response.ok) throw Error(response.statusText);
                return response.json();
            })
            .then((data) => {
                this.setState({
                    chats: data.chats,
                    num: data.num,
                    value: ''
                });
            })
            .catch((error) => console.log(error));
        event.preventDefault();
    }

    handleChange(event) {
        this.setState({ value: event.target.value });
    }

    handleStatus(event) {
        const { status } = this.state
        const { player, cmd, args } = JSON.parse(event.target.value);
        if (status == "PICK") {
            clearInterval(this.setChecker_obj);
        }
        else {
            this.setChecker_obj = setInterval(this.checkdbobj.bind(this), 500);
        }
        fetch(`/api/v1/sendcmd/`, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ player: player, cmd: cmd, args: args }),
        })
            .then((response) => {
                if (!response.ok) throw Error(response.statusText);
                return response.json();
            })
            .then((data) => {
                this.setState({
                    status: (status == "PICK") ? "DROP" : "PICK",
                });
            })
            .catch((error) => console.log(error));

    }

    handleNewInfo(event) {
        console.log("bug1")
        console.log(event.target.value)
        console.log(JSON.parse(event.target.value))
        const { player, task, objects, relation } = JSON.parse(event.target.value);
        fetch(`/api/v1/addInfo/`, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ player: player, task: task, objects: objects, relation: relation }),
        })
            .then((response) => {
                if (!response.ok) throw Error(response.statusText);
                return response.json();
            })
            .then({})
            .catch((error) => console.log(error));
    }

    render() {
        const { chats, value, obj, status, positions, task } = this.state
        const { canPick, canDrop, canShare, playerTurn } = this.state
        let vidUrl
        if (document.body.id == "player1" || document.body.id == "player_bot") {
            vidUrl = "/video1"
        }
        else if (document.body.id == "player2") {
            vidUrl = "/video2"
        }
        else {
            throw Error("wrong body id")
        }
        return (
            <div class="container">
                <div class="columns">
                    <div class="column is-3">
                        <TaskBox task={task} player={document.body.id} canShare={canShare} handleNewInfo={this.handleNewInfo} />
                    </div>

                    <div class="column is-5" id="vid">
                        <div>
                            <img src={vidUrl} />
                        </div>
                        <br/>
                        {!playerTurn || (playerTurn && !canPick && canDrop)
                            ? <div style={{ textAlign: 'center' }}>
                                <button class="button is-link is-medium" disabled>Finish my turn</button>
                            </div>
                            : <div style={{ textAlign: 'center' }}>
                                <button class="button is-link is-focused is-medium" onClick={this.changeTurn}>Finish my turn</button>
                            </div>
                        }
                    </div>

                    <div class="column" id="vid">
                        <ControlBox status={status} obj={obj} player={document.body.id} positions={positions} canPick={canPick} canDrop={canDrop} handleStatus={this.handleStatus} />
                        {document.body.id == "player1" || document.body.id == "player2"
                            ? <ChatBox player={document.body.id} chats={chats} value={value} handleChange={this.handleChange} handleNewComment={this.handleNewComment} />
                            : <InfoBox />
                        }
                    </div>
                </div>
            </div>
        );
    }
}



Post.propTypes = {
    url: PropTypes.string.isRequired,
    url2: PropTypes.string.isRequired
};


export default Post;

