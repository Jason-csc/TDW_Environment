import React from 'react';
import PropTypes from 'prop-types';

class Post extends React.Component {
    /* Display number of image and post owner of a single post
     */
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
        };
        this.handleNewComment = this.handleNewComment.bind(this);
        this.handleChange = this.handleChange.bind(this);
        this.handleStatus = this.handleStatus.bind(this);
    }



    componentDidMount() {
        this.setChecker = setInterval(this.checkdbchat.bind(this), 300);
        this.setChecker2 = setInterval(this.checkdbobj.bind(this), 400);
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
                    status: data.status,
                    task: data.task
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
                console.log(data);
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
                // this.setState({
                //     task: data.task
                // })
            })
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
        // console.log("handle status here");
        const { status } = this.state;
        // console.log(status);
        const { player, cmd, args } = JSON.parse(event.target.value);
        if (status == "PICK") {
            clearInterval(this.setChecker2);
        }
        else {
            this.setChecker2 = setInterval(this.checkdbobj.bind(this), 400);
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

    render() {
        const { chats, value, obj, status, positions, task } = this.state
        console.log(obj)
        console.log("task")
        console.log(task)
        // console.log(positions)
        let vidUrl
        if (document.body.id == "player1") {
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
                    <div class="column is-6" id="vid">
                        <div>
                            <img src={vidUrl} />
                        </div>
                        <div class="box">
                            <div style={{ height: '350px', overflowY: 'auto' }}>
                                <label class="label" style={{ fontSize: '1.7vw' }}>Complete Tasks Below</label>
                                {
                                    task.map((tk) => (
                                        <div class="box" key={tk}>
                                            {tk}
                                        </div>
                                    ))
                                }
                            </div>
                        </div>
                    </div>

                    <div>
                        <div class="box">
                            {status == "PICK"
                                ? <div style={{ height: '200px', overflowY: 'auto' }}>
                                    <label class="label" style={{ fontSize: '1.5vw'}}>Select Objects:</label>
                                    <label class="label" style={{ fontSize: '1.1vw' }}>Some objects are beyond your reach. You may ask your partner for help!</label>
                                    
                                    <div class="buttons" >
                                        {
                                            obj.map((object) => (
                                                object.reachable
                                                    ? <button class="button is-link is-outlined" value={JSON.stringify({ player: document.body.id, cmd: "pick", args: object.objectId })} onClick={this.handleStatus} >
                                                        {object.objectName}
                                                    </button>
                                                    : <button class="button is-link is-outlined" disabled>
                                                        {object.objectName} 
                                                        {/* {object.x} {object.y} {object.z} */}
                                                    </button>
                                            ))
                                        }
                                    </div>
                                    
                                </div>
                                : <div style={{ height: '200px', overflowY: 'auto' }}>
                                    <label class="label" style={{ fontSize: '1.4vw' }}>Select Where to place the object you're holding:</label>
                                    <div class="buttons" >
                                        {
                                            positions.map((position) => (
                                                <button class="button is-link is-outlined" value={JSON.stringify({ player: document.body.id, cmd: "drop", args: position.pos })} onClick={this.handleStatus} >
                                                    {position.name}
                                                </button>
                                            ))
                                        }
                                    </div>
                                </div>
                            }
                        </div>

                        <div class="box">
                            <div class="field">
                                <label class="label" style={{ fontSize: '1.7vw', width: '500px' }}>Chat box</label>
                                <div className="chat">
                                    <div style={{ height: '250px', overflowY: 'auto', display: "flex", flexDirection: "column-reverse" }}>
                                        {
                                            chats.map((singleChat) => (
                                                <div class="box" key={singleChat.chatid}>
                                                    <strong>{singleChat.owner.toUpperCase()}</strong> <small>{singleChat.created}</small>
                                                    <br />
                                                    {singleChat.text}
                                                </div>
                                            ))
                                        }
                                    </div>
                                    <form onSubmit={this.handleNewComment}>
                                        <div class="field">
                                            <strong>You ({document.body.id}) </strong>
                                            <div class="control">
                                                <textarea class="textarea" placeholder="Leave your message " value={value} onChange={this.handleChange}></textarea>
                                            </div>
                                        </div>
                                        <div class="control">
                                            <button class="button is-link">Submit</button>
                                        </div>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}



Post.propTypes = {
    url: PropTypes.string.isRequired,
    url2: PropTypes.string.isRequired,
};


export default Post;

