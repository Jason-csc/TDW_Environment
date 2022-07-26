import React from 'react';
import PropTypes from 'prop-types';


class ChatBox extends React.Component {
    constructor(props) {
        super(props);
        const { chats, player, value } = this.props
        this.state = {
            chats: chats,
            player: player,
            value: value,
        };

        this.handleTextChange = this.handleTextChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }


    handleTextChange(event) {
        const { handleChange } = this.props
        handleChange(event)
    }

    handleSubmit(event) {
        const { handleNewComment } = this.props
        handleNewComment(event)
    }

    render() {
        const { chats, player, value } = this.props
        return (
            <div class="box">
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
                        <form onSubmit={this.handleSubmit}>
                            <div class="field">
                                <strong>You ({player}) </strong>
                                <div class="control">
                                    <input class="input" type="text" placeholder="Leave your message " value={value} onChange={this.handleTextChange}></input>
                                </div>
                            </div>
                            <div class="control">
                                <button class="button is-link">Submit</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        )
    }

}



export default ChatBox;