import React from 'react';
import PropTypes from 'prop-types';



class ControlBox extends React.Component {
    constructor(props) {
        super(props);
        const { status, obj, player, positions, canPick, canDrop } = this.props
        this.state = {
            status: status,
            player: player,
            obj: obj,
            positions: positions,
            canPick: canPick,
            canDrop: canDrop,
        };

        this.handleChange = this.handleChange.bind(this);
    }


    handleChange(event) {
        const { handleStatus } = this.props
        handleStatus(event)
    }

    render() {
        const { status, obj, player, positions, canPick, canDrop } = this.props
        if (!canPick && !canDrop) {
            return (
                <div class="box" style={{ height: '155px'}}>
                    <label class="label" style={{ fontSize: '1.2vw' }}>Already place one object</label>
                    <label class="label" style={{ fontSize: '1.2vw' }}>Please wait for your next turn</label>
                </div>
            )
        } else {
            if (status == "PICK") {
                return (
                    <div class="box">
                        <div>
                            <label class="label" style={{ fontSize: '1.5vw' }}>Select Objects:</label>
                            <label class="label" style={{ fontSize: '1.1vw' }}>Some objects are beyond your reach. You may ask your partner for help!</label>
                            <div style={{ height: '140px', overflowY: 'auto' }}>
                                <div class="buttons" >
                                    {
                                        obj.map((object) => (
                                            object.reachable
                                                ? <button class="button is-link is-outlined" value={JSON.stringify({ player: player, cmd: "pick", args: object.objectId })} onClick={this.handleChange} >
                                                    {object.objectName}
                                                </button>
                                                : <button class="button is-link is-outlined" disabled>
                                                    {object.objectName}
                                                </button>
                                        ))
                                    }
                                </div>
                            </div>
                        </div>
                    </div>
                )
            } else {
                return (
                    <div class="box">
                        <div>
                            <label class="label" style={{ fontSize: '1.4vw' }}>Select Where to place the object you're holding:</label>
                            <div style={{ height: '130px', overflowY: 'auto' }}>
                                <div class="buttons" >
                                    {
                                        positions.map((position) => (
                                            <button class="button is-link is-outlined" value={JSON.stringify({ player: player, cmd: "drop", args: position.bin_id })} onClick={this.handleChange} >
                                                {position.name}
                                            </button>
                                        ))
                                    }
                                </div>
                            </div>
                        </div>
                    </div>
                )
            }
        }
    }
}


export default ControlBox;