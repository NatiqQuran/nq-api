import * as UploadType from "../types/upload";
import { AxiosResponse } from "axios";
import { Connection } from "../client/connection";
import { BaseController } from "../utils/baseController";
import { RequestConfig } from "../utils/globalTypes";

export class UploadSubjects extends BaseController {
    constructor(conn: Connection, token?: string) {
        super(conn, token);
    }
    /** GET /upload/subjects/ */
    async upload_subjects_list(config?: RequestConfig
    ): Promise<AxiosResponse<UploadType.UploadSubjectsResponseData>> {
        return await this.axiosGet(`/upload/subjects/`, config);
    }
}

export class UploadController extends BaseController {
    constructor(connection: Connection, token?: string) {
        super(connection, token);
    }
    
    /** POST /upload/ */
    async create(config?: RequestConfig<UploadType.UploadCreateRequestParams>
    ): Promise<AxiosResponse<any>> {
        return await this.axiosPost(`/upload/`, config);
    }
    
    subjects() {
        return new UploadSubjects(this.conn);
    }
}