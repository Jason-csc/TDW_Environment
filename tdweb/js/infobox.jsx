import React from 'react';
import PropTypes from 'prop-types';
import InfoPicture from './infopicture';

class InfoBox extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            shareInfo: []
        };

        this.setChecker_info = setInterval(this.checkshareInfo.bind(this), 500);
    }

    checkshareInfo() {
        fetch("/api/v1/shareInfo/", { credentials: 'same-origin' })
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
        const {shareInfo} = this.state
        // console.log("shared_info")
        // console.log(shareInfo)
        return (
            <div class="box">
                <label class="label" style={{ fontSize: '1.5vw' }}>Shared Info</label>
                <div style={{ height: '400px', width: '500px', overflowY: 'auto' }}>
                    {
                        shareInfo.map((si) => (
                            si.player == "player1"
                                ? <></>
                                : <article class="message is-info is-small">
                                    <div class="message-header">
                                        <p>Shared by {si.player}</p>
                                    </div>
                                    <div class="message-body" style={{ fontSize: '1.15vw', height: '70px', padding: '8px' }}>
                                        {/* {si.task} */}
                                        <InfoPicture tk={si} />
                                    </div>
                                </article>
                        ))
                    }
                </div>
            </div>
        )
    }
}


export default InfoBox;
