export interface SystemStatus {
    limit1: boolean;
    limit2: boolean;
    estop: boolean;
    running: boolean;
    led: boolean;
    calibrated: boolean;
    position: number;
    hq_preview: boolean;
    aux_preview: boolean;
}

export interface UsbDrive {
    device: string;
    mountpoint: string;
    fs_type: string;
    options: string;
    dump_freq: number;
    parallel_fsck: number;
}

export interface SensorCard {
    card_id: string;
    stage_offsets: int[];
    acquisition_time: string;
    subdir_path: string;
    image_format: "jpeg" | "png" | "tiff";
}

export interface CardIdResponse {
    // eslint-disable-next-line @typescript-eslint/naming-convention
    card_id: string;
    subdir: string;
}
