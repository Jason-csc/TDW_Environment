import React from 'react';

class InfoPicture extends React.Component {
    constructor(props) {
        super(props);
        const { tk } = this.props
        console.log("constuor")
        console.log(tk)
        this.state = {
            task: tk.task,
            objects: tk.objects,
            relation: tk.relation,
        };
    }

    getImg(name, path, type) {
        return path+name+type
    }

    render () {
        const {task, objects, relation } = this.state
        // TODO: convert objects list and relation into images
        return (
            <div style={{ flexDirection: 'row'}}>
                {objects.map((obj) => (
                    <image key={obj} src={require(this.getImg(obj, "./objImage/", ".png"))} style={{ height: '80px' }}></image>
                ))}
                <image src={require(this.getImg(relation, "./relationImage/", ".png"))} style={{ height: '80px' }} />
            </div>
        ) // For now, return the sentence (TO BE REPLACED)
    }

}

export default InfoPicture;