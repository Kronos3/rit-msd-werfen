export interface StageStatus {
    limit1: boolean;
    limit2: boolean;
    estop: boolean;
    running: boolean;
    led: boolean;
    calibrated: boolean;
    position: number;
}
