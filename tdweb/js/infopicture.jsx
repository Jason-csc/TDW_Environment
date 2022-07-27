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

    render () {
        const {task, objects, relation } = this.state
        // TODO: convert objects list and relation into images
        return task // For now, return the sentence (TO BE REPLACED)
    }

}

export default InfoPicture;