/* This file is part of Indico.
 * Copyright (C) 2002 - 2018 European Organization for Nuclear Research (CERN).
 *
 * Indico is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 3 of the
 * License, or (at your option) any later version.
 *
 * Indico is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Indico; if not, see <http://www.gnu.org/licenses/>.
 */

import _ from 'lodash';
import React from 'react';
import PropTypes from 'prop-types';
import {Card, Placeholder} from 'semantic-ui-react';


export default function CardPlaceholder() {
    return (
        <Card>
            <Placeholder>
                <Placeholder.Image />
            </Placeholder>
            <Card.Content>
                <Placeholder>
                    <Placeholder.Header>
                        <Placeholder.Line length="very short" />
                        <Placeholder.Line length="medium" />
                    </Placeholder.Header>
                    <Placeholder.Paragraph>
                        <Placeholder.Line length="short" />
                    </Placeholder.Paragraph>
                </Placeholder>
            </Card.Content>
            <Card.Content extra>
                <Placeholder>
                    <Placeholder.Line length="short" />
                </Placeholder>
            </Card.Content>
        </Card>
    );
}

function CardPlaceholderGroup({count, className}) {
    const props = className ? {className} : {};
    return (
        <Card.Group {...props} stackable>
            {_.range(0, count).map((i) => (
                <CardPlaceholder key={i} />
            ))}
        </Card.Group>
    );
}

CardPlaceholderGroup.propTypes = {
    count: PropTypes.number.isRequired,
    className: PropTypes.string
};

CardPlaceholderGroup.defaultProps = {
    className: null
};

CardPlaceholder.Group = CardPlaceholderGroup;
