import React from 'react';
import same from './images/same.png'
import different from './images/different.png'
import row from './images/row.png'
import column from './images/column.png'
import diagonal from './images/diagonal.png'
import bowl from './images/bowl.png'
import Black_Ball from './images/Black_Ball.png'
import Black_Battery from './images/Black_Battery.png'
import Black_Bowl from './images/Black_Bowl.png'
import Black_Pepper from './images/Black_Pepper.png'
import Blue_Bowl from './images/Blue_Bowl.png'
import Green_Ball from './images/Green_Ball.png'
import Green_Battery from './images/Green_Battery.png'
import Green_Bowl from './images/Green_Bowl.png'
import Green_Pepper from './images/Green_Pepper.png'
import Orange_Bowl from './images/Orange_Bowl.png'
import Red_Ball from './images/Red_Ball.png'
import Red_Battery from './images/Red_Battery.png'
import Red_Pepper from './images/Red_Pepper.png'

const images = {'same':same, 'different':different, 'row':row, 'column':column, 'diagonal':diagonal, 'bowl':bowl,
                'Black_Ball':Black_Ball, 'Black_Battery':Black_Battery, 'Black_Bowl':Black_Bowl, 'Black_Pepper':Black_Pepper,
                'Blue_Bowl':Blue_Bowl, 'Green_Ball':Green_Ball, 'Green_Battery':Green_Battery, 'Green_Bowl':Green_Bowl,
                'Green_Pepper':Green_Pepper, 'Orange_Bowl':Orange_Bowl, 'Red_Ball':Red_Ball, 'Red_Battery':Red_Battery, 'Red_Pepper':Red_Pepper}

class InfoPicture extends React.Component {
    constructor(props) {
        super(props);
        const { tk } = this.props
        this.state = {
            task: tk.task,
            objects: tk.objects,
            relation: tk.relation,
        };
    }

    importAll(r) {
        let images = {};
        r.keys().map((item, index) => { images[item.replace('./', '')] = r(item); });
        return images;
    }

    render () {
        const {task, objects, relation } = this.state
        console.log(relation)
        const allimgs = objects.concat(relation)
        // TODO: convert objects list and relation into images
        return (
            <div style={{ flexDirection: 'row', height: '80px'}}>
                {allimgs.map((obj) => (
                    <img key={obj} src={images[obj]} style={{ height: '80px' }} />
                ))}
                {/* {relation.map((rel) => {
                    <img key={rel} src={images[rel]} style={{ height: '80px' }} />
                })} */}
                
            </div>
        ) // For now, return the sentence (TO BE REPLACED)
    }

}

export default InfoPicture;