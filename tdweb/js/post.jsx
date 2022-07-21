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
            shareInfo: [],
        };
        this.handleNewComment = this.handleNewComment.bind(this);
        this.handleChange = this.handleChange.bind(this);
        this.handleStatus = this.handleStatus.bind(this);
        this.handleNewInfo = this.handleNewInfo.bind(this);
    }



    componentDidMount() {
        if (document.body.id == "player1" || document.body.id == "player2") {
            this.setChecker_chat = setInterval(this.checkdbchat.bind(this), 500);
        }
        else if (document.body.id == "player_bot") {
            this.setChecker_info = setInterval(this.checkshareInfo.bind(this), 500);
        }
        this.setChecker_obj = setInterval(this.checkdbobj.bind(this), 600);
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
            })
            .catch((error) => console.log(error));
    }

    checkshareInfo() {
        const { url3 } = this.props;
        fetch(url3, { credentials: 'same-origin' })
            .then((response) => {
                if (!response.ok) throw Error(response.statusText);
                return response.json();
            })
            .then((data) => {
                this.setState({
                    shareInfo: data.shareInfo,
                });
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
        const { player, info } = JSON.parse(event.target.value);
        fetch(`/api/v1/addInfo/`, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ player: player, info: info }),
        })
            .then((response) => {
                if (!response.ok) throw Error(response.statusText);
                return response.json();
            })
            .then((data) => {
                this.setState({
                    shareInfo: data.shareInfo,
                });
            })
            .catch((error) => console.log(error));
    }

    render() {
        const { chats, value, obj, status, positions, task, shareInfo } = this.state
        const mode = Boolean(document.body.id == "player1" || document.body.id == "player2")
        console.log(mode)
        console.log(shareInfo)
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
                        {mode
                            ? <div>
                                <label class="label" style={{ fontSize: '1.5vw' }}>Complete Tasks Below</label>
                                <div style={{ height: '500px', overflowY: 'auto' }}>
                                    <article class="message is-dark">
                                        {
                                            task.map((tk) => (
                                                <div key={tk.task} class="message-body is-dark" style={{ fontSize: '1.1vw' }}>
                                                    {tk.task}
                                                </div>
                                            ))
                                        }
                                    </article>
                                </div>
                            </div>
                            : <div style={{ height: '500px' }}>
                                <label class="label" style={{ fontSize: '1.5vw' }}>Complete Tasks Below</label>
                                <label class="label" style={{ fontSize: '1.3vw' }}>You can click to share with your partner</label>
                                {/* <div class="buttons" > */}
                                {
                                    task.map((tk) => (
                                        <div style={{ fontSize: '1.1vw' }}>
                                            <button class="js-modal-trigger" value={JSON.stringify({ player: document.body.id, info: tk.task })} onClick={this.handleNewInfo} style={{ fontSize: '1.1vw', backgroundColor: `hsl(0, 0%, 87%)`, height: '80px', borderStyle: 'none'}}>
                                                {tk.task}
                                            </button>
                                            <br />
                                            <br />
                                        </div>
                                    ))
                                }
                                {/* </div> */}
                            </div>
                        }
                    </div>

                    <div class="column is-5" id="vid">
                        <div>
                            <img src={vidUrl} />
                        </div>
                    </div>

                    <div class="column" id="vid">
                        <div class="box">
                            {status == "PICK"
                                ? <div>
                                    <label class="label" style={{ fontSize: '1.5vw' }}>Select Objects:</label>
                                    <label class="label" style={{ fontSize: '1.1vw' }}>Some objects are beyond your reach. You may ask your partner for help!</label>
                                    <div style={{ height: '140px', overflowY: 'auto' }}>
                                        <div class="buttons" >
                                            {
                                                obj.map((object) => (
                                                    object.reachable
                                                        ? <button class="button is-link is-outlined" value={JSON.stringify({ player: document.body.id, cmd: "pick", args: [object.objectId, object.x] })} onClick={this.handleStatus} >
                                                            {object.objectName}
                                                            {/* {object.x} {object.y} {object.z} */}
                                                        </button>
                                                        : <button class="button is-link is-outlined" disabled>
                                                            {object.objectName}
                                                            {/* {object.x} {object.y} {object.z} */}
                                                        </button>
                                                ))
                                            }
                                        </div>
                                    </div>
                                </div>
                                : <div>
                                    <label class="label" style={{ fontSize: '1.4vw' }}>Select Where to place the object you're holding:</label>
                                    <div style={{ height: '130px', overflowY: 'auto' }}>
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
                                </div>
                            }
                        </div>
                        {mode
                            ? <div class="box">
                                <div class="field">
                                    <label class="label" style={{ fontSize: '1.5vw', width: '500px' }}>Chat box</label>
                                    <div className="chat">
                                        <div style={{ height: '200px', overflowY: 'auto', display: "flex", flexDirection: "column-reverse" }}>
                                            {
                                                chats.map((singleChat) => (
                                                    singleChat.owner == "player1"
                                                        ? <article class="message is-success">
                                                            <div class="message-body" key={singleChat.chatid}>
                                                                <strong>{singleChat.owner.toUpperCase()}</strong> <small>{singleChat.created}</small>
                                                                <br />
                                                                {singleChat.text}
                                                            </div>
                                                        </article>
                                                        : <article class="message is-info">
                                                            <div class="message-body" key={singleChat.chatid}>
                                                                <strong>{singleChat.owner.toUpperCase()}</strong> <small>{singleChat.created}</small>
                                                                <br />
                                                                {singleChat.text}
                                                            </div>
                                                        </article>
                                                ))
                                            }
                                        </div>
                                        <form onSubmit={this.handleNewComment}>
                                            <div class="field">
                                                <strong>You ({document.body.id}) </strong>
                                                <div class="control">
                                                    <input class="input" type="text" placeholder="Leave your message " value={value} onChange={this.handleChange}></input>
                                                </div>
                                            </div>
                                            <div class="control">
                                                <button class="button is-link">Submit</button>
                                            </div>
                                        </form>
                                    </div>
                                </div>
                            </div>
                            : <div class="box">
                                <label class="label" style={{ fontSize: '1.5vw' }}>Shared Info</label>
                                <div style={{ height: '400px', width: '500px', overflowY: 'auto' }}>
                                    {
                                        shareInfo.map((si) => (
                                            si.player == document.body.id
                                                ? <article class="message is-small">
                                                    <div class="message-header">
                                                        <p>Shared by You</p>
                                                    </div>
                                                    <div class="message-body" style={{ fontSize: '1.15vw', height: '75px' }}>
                                                        {si.info}
                                                    </div>
                                                </article>
                                                : <article class="message is-info is-small">
                                                    <div class="message-header">
                                                        <p>Shared by {si.player}</p>
                                                    </div>
                                                    <div class="message-body" style={{ fontSize: '1.15vw', height: '75px'}}>
                                                        {si.info}
                                                    </div>
                                                </article>
                                        ))
                                    }
                                </div>
                            </div>
                        }
                    </div>
                </div>
            </div>
        );
    }
}



Post.propTypes = {
    url: PropTypes.string.isRequired,
    url2: PropTypes.string.isRequired,
    url3: PropTypes.string.isRequired,
};


export default Post;

