pragma Singleton

import QtQuick

QtObject {
    id: root

    readonly property QtObject light: QtObject {
        readonly property color bgCanvas: #eff0f1
        readonly property color bgSurface: #f7f7f8
        readonly property color bgRaised: #f7f7f8
        readonly property color bgOverlay: #f7f7f8
        readonly property color bgSunken: #e0e2e5
        readonly property color bgGlass: Qt.rgba(255, 255, 255, 0.55)
        readonly property color bgGlassStrong: Qt.rgba(255, 255, 255, 0.72)
        readonly property color fgDefault: #3c3d40
        readonly property color fgMuted: #585b62
        readonly property color fgSubtle: #696c72
        readonly property color fgOnAccent: #ffffff
        readonly property color borderSubtle: #e0e2e5
        readonly property color borderDefault: #cdcfd4
        readonly property color borderStrong: #b3b6bd
        readonly property color borderGlassEdge: Qt.rgba(255, 255, 255, 0.9)
        readonly property color accentDefault: #2c3fe0
        readonly property color accentHover: #3f5ac0
        readonly property color accentActive: #344990
        readonly property color accentSubtle: #ebf0f8
        readonly property color accentMuted: #d6e2ff
        readonly property color success: #389152
        readonly property color warning: #a77000
        readonly property color destructive: #c94f4b
        readonly property color destructiveHover: #a0423e
        readonly property color selection: #eaf0ff
        readonly property color focusRing: #6e90ff
    }

    readonly property QtObject dark: QtObject {
        readonly property color bgCanvas: #232425
        readonly property color bgSurface: #3c3d40
        readonly property color bgRaised: #4d4f54
        readonly property color bgOverlay: #4d4f54
        readonly property color bgSunken: #232425
        readonly property color bgGlass: Qt.rgba(18, 20, 28, 0.55)
        readonly property color bgGlassStrong: Qt.rgba(18, 20, 28, 0.72)
        readonly property color fgDefault: #eff0f1
        readonly property color fgMuted: #b3b6bd
        readonly property color fgSubtle: #9598a2
        readonly property color fgOnAccent: #232425
        readonly property color borderSubtle: #4d4f54
        readonly property color borderDefault: #62656b
        readonly property color borderStrong: #797d85
        readonly property color borderGlassEdge: Qt.rgba(255, 255, 255, 0.14)
        readonly property color accentDefault: #a3afff
        readonly property color accentHover: #c0d0e9
        readonly property color accentActive: #d8e3f2
        readonly property color accentSubtle: #1b2339
        readonly property color accentMuted: #344990
        readonly property color success: #83c992
        readonly property color warning: #e0ab5d
        readonly property color destructive: #fe948c
        readonly property color destructiveHover: #ffbbb5
        readonly property color selection: #2b3a68
        readonly property color focusRing: #a0b7db
    }

    readonly property QtObject radius: QtObject {
        readonly property int $comment: §7.1 specifies ~34px on panels. That is the signature value — everything else scales down from it.
        readonly property int none: 0
        readonly property int xs: 6
        readonly property int sm: 10
        readonly property int md: 14
        readonly property int lg: 20
        readonly property int xl: 28
        readonly property int panel: 34
        readonly property int pill: 999
    }
    readonly property QtObject space: QtObject {
        readonly property int $comment: 4px base grid. Nothing in the system should introduce a value that is not a multiple of 4.
        readonly property int none: 0
        readonly property int 2xs: 2
        readonly property int xs: 4
        readonly property int sm: 8
        readonly property int md: 12
        readonly property int lg: 16
        readonly property int xl: 20
        readonly property int 2xl: 24
        readonly property int 3xl: 32
        readonly property int 4xl: 40
        readonly property int 5xl: 48
        readonly property int 6xl: 64
        readonly property int 7xl: 80
        readonly property int 8xl: 96
    }
    readonly property QtObject duration: QtObject {
        readonly property int instant: 0
        readonly property int quick: 120
        readonly property int standard: 200
        readonly property int emphasized: 300
        readonly property int slow: 420
        readonly property int deliberate: 600
    }
    readonly property QtObject glass: QtObject {
        readonly property int saturation: 180
        readonly property QtObject variants: QtObject {
            readonly property QtObject panel: QtObject {
                readonly property int blur: 40
                readonly property int radius: 34
                readonly property int edgeWidth: 1
            }
            readonly property QtObject dock: QtObject {
                readonly property int blur: 32
                readonly property int radius: 34
                readonly property int edgeWidth: 1
            }
            readonly property QtObject launcher: QtObject {
                readonly property int blur: 44
                readonly property int radius: 34
                readonly property int edgeWidth: 1
            }
            readonly property QtObject popover: QtObject {
                readonly property int blur: 28
                readonly property int radius: 20
                readonly property int edgeWidth: 1
            }
            readonly property QtObject statusPill: QtObject {
                readonly property int blur: 24
                readonly property int radius: 999
                readonly property int edgeWidth: 1
            }
        }
    }
    readonly property QtObject typography: QtObject {
        readonly property QtObject displayLg: QtObject {
            readonly property int pixelSize: 40
            readonly property int lineHeight: 48
            readonly property int weight: 620
            readonly property real tracking: -0.022
        }
        readonly property QtObject displayMd: QtObject {
            readonly property int pixelSize: 32
            readonly property int lineHeight: 40
            readonly property int weight: 620
            readonly property real tracking: -0.018
        }
        readonly property QtObject titleLg: QtObject {
            readonly property int pixelSize: 24
            readonly property int lineHeight: 32
            readonly property int weight: 600
            readonly property real tracking: -0.014
        }
        readonly property QtObject titleMd: QtObject {
            readonly property int pixelSize: 20
            readonly property int lineHeight: 28
            readonly property int weight: 600
            readonly property real tracking: -0.012
        }
        readonly property QtObject titleSm: QtObject {
            readonly property int pixelSize: 16
            readonly property int lineHeight: 24
            readonly property int weight: 600
            readonly property real tracking: -0.008
        }
        readonly property QtObject bodyLg: QtObject {
            readonly property int pixelSize: 16
            readonly property int lineHeight: 26
            readonly property int weight: 400
            readonly property real tracking: 0
        }
        readonly property QtObject bodyMd: QtObject {
            readonly property int pixelSize: 14
            readonly property int lineHeight: 21
            readonly property int weight: 400
            readonly property real tracking: 0
        }
        readonly property QtObject bodySm: QtObject {
            readonly property int pixelSize: 13
            readonly property int lineHeight: 19
            readonly property int weight: 400
            readonly property real tracking: 0
        }
        readonly property QtObject labelLg: QtObject {
            readonly property int pixelSize: 15
            readonly property int lineHeight: 20
            readonly property int weight: 500
            readonly property real tracking: 0.002
        }
        readonly property QtObject labelMd: QtObject {
            readonly property int pixelSize: 13
            readonly property int lineHeight: 17
            readonly property int weight: 500
            readonly property real tracking: 0.01
        }
        readonly property QtObject labelSm: QtObject {
            readonly property int pixelSize: 11
            readonly property int lineHeight: 14
            readonly property int weight: 600
            readonly property real tracking: 0.04
        }
        readonly property QtObject monoMd: QtObject {
            readonly property int pixelSize: 13
            readonly property int lineHeight: 21
            readonly property int weight: 400
            readonly property real tracking: 0
        }
        readonly property QtObject monoLg: QtObject {
            readonly property int pixelSize: 15
            readonly property int lineHeight: 24
            readonly property int weight: 400
            readonly property real tracking: 0
        }
    }
}
