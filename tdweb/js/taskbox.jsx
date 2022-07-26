import React from 'react';
import PropTypes from 'prop-types';

class TaskBox extends React.Component {
    constructor(props) {
        super(props);
        const { task, player, canShare } = this.props
        this.state = {
            task: task,
            player: player,
            canShare: canShare,
        };

        this.handleInfo = this.handleInfo.bind(this);
    }

    handleInfo(event) {
        const { handleNewInfo } = this.props
        handleNewInfo(event)
    }


    render() {
        const { task, player, canShare } = this.props
        const mode = Boolean(player == "player1" || player == "player2")
        if (mode) {
            return (
                <div>
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
            )
        } else {
            if (canShare) {
                return (
                    <div style={{ height: '500px' }}>
                        <label class="label" style={{ fontSize: '1.5vw' }}>Complete Tasks Below</label>
                        <label class="label" style={{ fontSize: '1.3vw' }}>You can click to share with your partner</label>
                        {
                            task.map((tk) => (
                                tk.shared
                                    ? <div>
                                        <button style={{ fontSize: '1.1vw', backgroundColor: `hsl(0, 0%, 85%)`, height: '80px', borderStyle: 'none' }} disabled>
                                            {tk.task}
                                        </button>
                                        <br />
                                        <br />
                                    </div>
                                    : <div>
                                        <button class="js-modal-trigger" value={JSON.stringify({ player: player, info: tk.task })} onClick={this.handleInfo} style={{ fontSize: '1.1vw', backgroundColor: `hsl(0, 0%, 85%)`, height: '80px', borderStyle: 'none' }}>
                                            {tk.task}
                                        </button>
                                        <br />
                                        <br />
                                    </div>
                            ))
                        }
                    </div>
                )
            } else {
                return (
                    <div style={{ height: '500px' }}>
                        <label class="label" style={{ fontSize: '1.2vw' }}>Successfully share your information to your partner </label>
                        <label class="label" style={{ fontSize: '1.2vw' }}>Please wait for your next turn </label>
                        {
                            task.map((tk) => (
                                tk.shared
                                    ? <div>
                                        <button style={{ fontSize: '1.1vw', borderColor: `hsl(0, 0%, 90%)`, height: '80px', borderStyle: 'solid' }} disabled>
                                            {tk.task}
                                        </button>
                                        <br />
                                        <br />
                                    </div>
                                    : <div>
                                        <button style={{ fontSize: '1.1vw', borderColor: `hsl(0, 0%, 75%)`, height: '80px', borderStyle: 'solid' }} disabled>
                                            {tk.task}
                                        </button>
                                        <br />
                                        <br />
                                    </div>
                            ))
                        }
                    </div>
                )
            }

        }
    }

}


export default TaskBox;