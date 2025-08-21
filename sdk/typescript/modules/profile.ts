import * as ProfileType from "../types/profile";
import { AxiosResponse } from "axios";
import { Connection } from "../client/connection";
import { BaseController } from "../utils/baseController";
import { RequestConfig } from "../utils/globalTypes";

export class ProfileMe extends BaseController {
    constructor(conn: Connection, token?: string) {
        super(conn, token);
    }
    /** GET /profile/me/ */
    async profile_me_retrieve(config?: RequestConfig
    ): Promise<AxiosResponse<ProfileType.ProfileMeResponseData>> {
        return await this.axiosGet(`/profile/me/`, config);
    }
    /** POST /profile/me/ */
    async profile_me_create(data: ProfileType.ProfileMeRequestData, config?: RequestConfig
    ): Promise<AxiosResponse<ProfileType.ProfileMeResponseData>> {
        return await this.axiosPost(`/profile/me/`, data, config);
    }
}

export class ProfileController extends BaseController {
    public readonly me: ProfileMe;

    constructor(connection: Connection, token?: string) {
        super(connection, token);
        this.me = new ProfileMe(this.conn);
    }
    
    /** GET /profile/{uuid}/ */
    async retrieve(uuid: string,config?: RequestConfig
    ): Promise<AxiosResponse<ProfileType.ProfileRetrieveResponseData>> {
        return await this.axiosGet(`/profile/${uuid}/`, config);
    }
    
}