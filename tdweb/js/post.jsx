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
        };
        this.handleNewComment = this.handleNewComment.bind(this);
        this.handleChange = this.handleChange.bind(this);
    }

    componentDidMount() {
        this.setChecker = setInterval(this.checkdbchat.bind(this), 200);
        const { url } = this.props;
        fetch(url, { credentials: 'same-origin' })
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
                        value: ''
                    });
                }
            })
            .catch((error) => console.log(error));


    }

    handleNewComment(event) {
        const { value } = this.state;
        fetch(`/api/v1/chats/`,
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


    render() {
        const { chats, value } = this.state;
        const video_url = 'video_' + document.body.id;
        console.log(video_url);
        return (
            <div class="column">
                <div class="box">
                    <div class="field">
                        <label class="label" style={{ fontSize: '2vw', width: '500px' }}>Chat box</label>
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

        );
    }
}



Post.propTypes = {
    url: PropTypes.string.isRequired,
};


export default Post;

