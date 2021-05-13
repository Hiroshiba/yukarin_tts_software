import QtQuick 2.15
import QtQuick.Window 2.2
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Window {
    id: root

    width: 640
    height: 480
    visible: true

    required property var audioModel

    signal play(int index)

    signal undo()
    signal redo()
    signal addAudioItem()
    signal modifyAudioItem(int index, string key, string value)

    signal showUndoStack()

    Shortcut {
        sequence: StandardKey.Undo
        onActivated: undo()
    }
    Shortcut {
        sequence: StandardKey.Redo
        onActivated: redo()
    }

    Shortcut {
        sequence: StandardKey.Print
        onActivated: showUndoStack()
    }

    ListView {
        id: audioList

        anchors.fill: parent
        model: root.audioModel

        delegate: Item {
            id: audioItem

            required property int index
            required property string text
            required property bool playing
            
            width: ListView.view.width
            height: 50

            RowLayout {
                anchors.fill: parent

                RoundButton {
                    width: height
                    height: height

                    text: playing ? "■" : "▶"

                    onClicked: {
                        play(index)
                    }
                }

                TextInput {
                    id: textInput

                    default property string beforeText: ""

                    Layout.fillWidth: true
                    text: audioItem.text

                    onFocusChanged: {
                        if ( focus ) {
                            beforeText = text
                        } else {
                            if ( beforeText !== text ) {
                                modifyAudioItem(index, "text", text)
                            }
                        }
                    }

                    onEditingFinished: {
                        focus = false
                    }
                }
            }
        }

        footer: Item {
            width: parent.width
            height: 50

            Button {
                width: 80
                height: 30
                anchors.verticalCenter: parent.verticalCenter
                anchors.horizontalCenter: parent.horizontalCenter

                text: "追加"

                onClicked: {
                    addAudioItem()
                }
            }
        }
    }
}
